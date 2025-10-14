# -*- coding: utf-8 -*-
#
# Copyright 2021-2025 NXP
#
# SPDX-License-Identifier: MIT


import asyncio
import logging
import os

from fc_server.core.decorators import (
    check_priority_scheduler,
    check_seize_strategy,
    safe_cache,
)
from fc_server.core.plugin import FCPlugin
from fc_server.plugins.utils.labgrid import Labgrid


class Plugin(FCPlugin, Labgrid):
    """
    Plugin for [labgrid framework](https://github.com/labgrid-project/labgrid)
    """

    def __init__(self, frameworks_config):
        super().__init__()
        self.schedule_interval = 2  # poll labgrid reserve queues every 2 seconds

        os.environ["LG_CROSSBAR"] = frameworks_config["lg_crossbar"]
        os.environ["LG_HOSTNAME"] = "fc"
        os.environ["LG_USERNAME"] = "fc"

        self.managed_resources = None

        self.seize_cache = {}  # cache to avoid busy seize

        self.logger = logging.getLogger("fc_server")

    @safe_cache
    def __update_cache(self, cache_name, job_id, value):
        self.__dict__[cache_name][job_id] += value

    async def __labgrid_guard_reservation(self, resource):
        self.logger.info("* [start] inject guard reservation for %s", resource)
        await self.labgrid_create_reservation(resource, priority=-100)
        self.logger.info("* [done] inject guard reservation for %s", resource)

    async def __labgrid_system_reservation(self, driver, resource):
        self.logger.info("* [start] inject system reservation for %s", resource)
        ret, _, _ = await self.labgrid_create_reservation(
            resource, priority=100, wait=True
        )
        if ret != 0:
            self.logger.info("* [exit] inject system reservation for %s", resource)
            return

        ret, _, _ = await self.labgrid_acquire_place(resource)
        if ret != 0:
            self.logger.info("* [exit] inject system reservation for %s", resource)
            return

        self.logger.info("* [done] inject system reservation for %s", resource)

        await driver.return_resource(resource, self)

    async def __labgrid_init(self, driver, resource, semaphore):
        """
        Let FC take over by inject special reservation
        """
        async with semaphore:
            system_reservation_found = False

            reservations = await self.labgrid_get_reservations()
            if reservations:
                for _, v in reservations.items():  # pylint: disable=invalid-name
                    if (
                        v["filters"]["main"] == f"name={resource}"
                        and v["owner"] == "fc/fc"
                        and v["prio"] == 100.0
                    ):
                        if v["state"] == "acquired":
                            # do nothing if system reservation already there
                            self.logger.info("- %s system reservation exist", resource)
                            system_reservation_found = True
                        else:
                            await self.labgrid_cancel_reservation(v["token"])

            if not system_reservation_found:
                # add system reservation for bare lock which previously not in FC control
                # or system reservation expired
                _, reservation = await self.labgrid_create_reservation(
                    resource, priority=100, shell=True
                )

                ret, _, _ = await self.labgrid_acquire_place(resource)
                if ret != 0:
                    # either this resource directly be locked before FC take control,
                    # or fall into schedule gap when FC restart
                    if reservation:
                        await self.labgrid_cancel_reservation(reservation)
                    asyncio.create_task(
                        self.__labgrid_system_reservation(driver, resource)
                    )
                    self.logger.info("- %s system reservation scheduled", resource)
                else:
                    self.logger.info("- %s system reservation ready", resource)

            # set correct resource status
            owner = await self.labgrid_get_place_owner(resource)
            if owner != "fc/fc":
                driver.accept_resource(resource, self, purpose="amend")
            else:
                await driver.return_resource(resource, self)

    async def force_kick_off(self, resource):
        """
        Allow coordinator to seize labgrid resource
        """

        self.logger.info("Labgrid: force kick off %s", resource)

        token = await self.labgrid_get_place_token(resource)

        if token:
            reservations = await self.labgrid_get_reservations()

            if reservations:
                for reservation in reservations.keys():
                    if reservation == f"Reservation '{token}'":
                        await self.labgrid_cancel_reservation(token)
                        await self.labgrid_release_place(resource, True)
                        break

    async def lock_info(self, driver):
        """
        Current lock info of this framework
        """

        locks_text = await self.labgrid_get_lock_info()

        locks_text_list = []
        header = True
        anchor = -1
        for lock_text in locks_text.splitlines():
            if header:
                anchor = lock_text.find("Place")
                locks_text_list.append(lock_text)
                header = False
                continue

            if lock_text[anchor:].split(" ")[0] in driver.managed_resources:
                locks_text_list.append(lock_text)

        if len(locks_text_list) == 1:
            return None

        return "\n".join(locks_text_list)

    async def get_resource_owner(self, resource):
        for _ in range(10):
            await asyncio.sleep(1)
            owner = await self.labgrid_get_place_owner(resource)
            if owner and owner not in ("", "fc/fc", "None"):
                return owner.split("/", 1)[1] if "/" in owner else owner
        return "unknown"

    async def __seize_resource(self, driver, job_id, candidated_resources):
        """
        Request coordinator to seize low priority resource
        """

        if candidated_resources:
            priority_resources = await driver.coordinate_resources(
                self, job_id, *candidated_resources
            )
            if priority_resources:
                self.__update_cache("seize_cache", job_id, priority_resources)

    async def schedule(
        self, driver
    ):  # pylint: disable=too-many-branches, too-many-statements, too-many-locals
        """
        Monitor Labgrid reserve queue, once have pending reservation,
        release current fc acquisition to let normal user acquire the device
        Coodinator will call this function periodly
        """

        async def switch_from_fc_to_labgrid(resource):
            # if user release quickly, there possible be a window period during user release and
            # system reservation, to avoid this low probablity issue,
            # inject a low priority reservation to protect it
            await self.__labgrid_guard_reservation(resource)

            reservation = managed_resources_tokens.get(resource, None)
            if reservation:
                await self.labgrid_cancel_reservation(reservation)
            else:
                self.logger.warning(
                    "No reservation for %s found, this possible result in issue",
                    resource,
                )
            await self.labgrid_release_place(resource)

            # inject a high priority system reservation to let FC lock the device
            # after normal user finish using the device
            asyncio.create_task(self.__labgrid_system_reservation(driver, resource))

        # query labgrid reservations
        guard_reservations = set()
        system_reservations = set()
        managed_resources_tokens = {}
        reservations = await self.labgrid_get_reservations()
        if reservations:
            # collect system reservation entries per resource so we can
            # apply the new dedupe rules per-resource after scanning all
            system_entries = {}
            for _, v in reservations.items():  # pylint: disable=invalid-name
                resource = v["filters"]["main"][5:]
                if v["owner"] == "fc/fc" and v["state"] in ("acquired", "allocated"):
                    managed_resources_tokens[resource] = v["token"]

                # free outdated guard reservations to prevent block due to user does quick release
                if (
                    v["owner"] == "fc/fc"
                    and v["state"] == "allocated"
                    and v["prio"] == -100.0
                ):
                    self.logger.warning(
                        "Free outdated guard reservation for %s", resource
                    )
                    await self.__labgrid_guard_reservation(resource)
                    await self.labgrid_cancel_reservation(v["token"])

                # collect system reservations (prio == 100) for later per-resource processing
                if (
                    v["owner"] == "fc/fc"
                    and v["state"] in ("waiting", "allocated", "acquired")
                    and v["prio"] == 100.0
                ):
                    system_entries.setdefault(resource, []).append(v)

                # record guard reservations
                if (
                    v["owner"] == "fc/fc"
                    and v["state"] in ("waiting", "allocated")
                    and v["prio"] == -100.0
                ):
                    guard_reservations.add(resource)

            # enforce per-resource rules for system reservations:
            # 1) if all waiting -> keep one waiting, cancel others
            # 2) if any allocated -> keep one allocated, cancel waiting ones
            # 3) if any acquired -> keep one acquired, cancel others
            for resource, entries in system_entries.items():
                # build simple lists for state checks
                acquired = [e for e in entries if e.get("state") == "acquired"]
                allocated = [e for e in entries if e.get("state") == "allocated"]
                waiting = [e for e in entries if e.get("state") == "waiting"]

                # prefer acquired > allocated > waiting
                if acquired:
                    # keep the first acquired, cancel all other entries for this resource
                    keep = acquired[0]
                    for entry in entries:
                        if entry is keep:
                            continue
                        self.logger.warning(
                            "Free duplicate system reservation for %s (token=%s)",
                            resource,
                            entry.get("token"),
                        )
                        await self.labgrid_cancel_reservation(entry.get("token"))
                    system_reservations.add(resource)
                elif allocated:
                    # keep one allocated, cancel waiting ones
                    keep = allocated[0]
                    for entry in waiting:
                        self.logger.warning(
                            "Free duplicate system reservation for %s (token=%s)",
                            resource,
                            entry.get("token"),
                        )
                        await self.labgrid_cancel_reservation(entry.get("token"))
                    system_reservations.add(resource)
                else:
                    # all waiting: keep the first waiting and cancel the rest
                    if waiting:
                        keep = waiting[0]
                        for entry in waiting[1:]:
                            self.logger.warning(
                                "Free duplicate system reservation for %s (token=%s)",
                                resource,
                                entry.get("token"),
                            )
                            await self.labgrid_cancel_reservation(entry.get("token"))
                        system_reservations.add(resource)

            # amend system reservation in case some race condition removed the system reservation
            # e.g.
            # 1. exporter restart in process, fc fail to add system reservation when restart
            # 2. user release lock during the exporter restart, scheduled system reservation failed
            for managed_resource in self.managed_resources:
                if (
                    managed_resource not in system_reservations
                    and managed_resource not in guard_reservations
                ):
                    self.logger.warning(
                        "Setup missed system reservation for %s", managed_resource
                    )
                    await self.__labgrid_guard_reservation(managed_resource)
                    await self.labgrid_release_place(managed_resource)
                    asyncio.create_task(
                        self.__labgrid_system_reservation(driver, managed_resource)
                    )

            # start user reservation handle
            resource_list = []
            for _, v in reservations.items():  # pylint: disable=invalid-name
                resource = v["filters"]["main"][5:]
                if v["owner"] != "fc/fc" and v["state"] == "waiting":
                    if await driver.is_resource_available(self, resource):
                        if driver.is_seized_resource(self, resource):
                            driver.clear_seized_job_records(resource)

                        # if has pending reservation not belongs to normal user
                        # meanwhile device currently belongs to fc, accept it
                        driver.accept_resource(resource, self)
                        resource_list.append(resource)
                    else:
                        job_id = v["token"]

                        # pylint: disable=cell-var-from-loop
                        @check_priority_scheduler(driver)
                        @check_seize_strategy(driver, self)
                        @safe_cache
                        def labgrid_seize_resource(*_):
                            candidated_resources = (
                                []
                                if resource in self.seize_cache[job_id]
                                else [resource]
                            )

                            if (
                                not driver.is_seized_job(job_id)
                                and candidated_resources
                            ):
                                # no available resource found, try to seize from other framework
                                asyncio.create_task(
                                    self.__seize_resource(
                                        driver, job_id, candidated_resources
                                    )
                                )

                        labgrid_seize_resource(self, "seize_cache", job_id)

            if resource_list:
                await asyncio.gather(
                    *[
                        switch_from_fc_to_labgrid(resource)
                        for resource in set(resource_list)
                    ]
                )
        elif reservations == "":
            # amend system reservation due to coordinator restart
            for managed_resource in self.managed_resources:
                self.logger.warning(
                    "Setup missed system reservation for %s due to coordinator restart",
                    managed_resource,
                )
                await self.labgrid_create_reservation(
                    managed_resource, priority=100, shell=True
                )
                await self.labgrid_acquire_place(managed_resource)

                # set correct resource status
                owner = await self.labgrid_get_place_owner(managed_resource)
                if owner != "fc/fc":
                    driver.accept_resource(managed_resource, self, purpose="amend")
                else:
                    await driver.return_resource(managed_resource, self)

    async def init(self, driver):
        """
        Generate and return tasks to let fc own specified labgrid devices
        This be called only once when coordinator start
        """

        places = await self.labgrid_get_places()
        self.managed_resources = [
            place for place in places if place in driver.managed_resources
        ]
        candidated_init_resources = self.managed_resources.copy()

        task_semaphore = asyncio.Semaphore(20)
        return [
            self.__labgrid_init(driver, resource, task_semaphore)
            for resource in candidated_init_resources
        ]
