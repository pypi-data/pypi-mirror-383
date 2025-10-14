# -----------------------------------------------------------------------------
# Copyright (c) 2025, Oracle and/or its affiliates.
#
# Licensed under the Universal Permissive License v 1.0 as shown at
# http://oss.oracle.com/licenses/upl.
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# async/disable_ai_provider.py
#
# Async API to disable AI provider for database users
# -----------------------------------------------------------------------------

import asyncio
import os

import select_ai

admin_user = os.getenv("SELECT_AI_ADMIN_USER")
password = os.getenv("SELECT_AI_ADMIN_PASSWORD")
dsn = os.getenv("SELECT_AI_DB_CONNECT_STRING")
select_ai_user = os.getenv("SELECT_AI_USER")


async def main():
    await select_ai.async_connect(user=admin_user, password=password, dsn=dsn)
    await select_ai.async_disable_provider(
        users=select_ai_user, provider_endpoint="*.openai.azure.com"
    )
    print("Disabled AI provider for user: ", select_ai_user)


asyncio.run(main())
