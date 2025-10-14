# Copyright Contributors to the Testing Farm project.
# SPDX-License-Identifier: Apache-2.0

from dynaconf import LazySettings  # type: ignore

settings = LazySettings(
    # all environment variables have `TESTING_FARM_` prefix
    ENVVAR_PREFIX_FOR_DYNACONF="TESTING_FARM",
    # defaults
    API_URL="https://api.dev.testing-farm.io/v0.1",
    INTERNAL_API_URL="https://internal.api.dev.testing-farm.io/v0.1",
    API_TOKEN=None,
    # Restart command specific source API configuration (fallback to general settings)
    SOURCE_API_URL=None,
    INTERNAL_SOURCE_API_URL=None,
    SOURCE_API_TOKEN=None,
    # Restart command specific target API configuration (fallback to general settings)
    TARGET_API_URL=None,
    TARGET_API_TOKEN=None,
    ISSUE_TRACKER="https://gitlab.com/testing-farm/general/-/issues/new",
    STATUS_PAGE="https://status.testing-farm.io",
    ONBOARDING_DOCS="https://docs.testing-farm.io/Testing%20Farm/0.1/onboarding.html",
    CONTAINER_SIGN="/.testing-farm-container",
    WATCH_TICK=30,
    DEFAULT_API_TIMEOUT=10,
    DEFAULT_API_RETRIES=7,
    # default reservation duration in minutes
    DEFAULT_RESERVATION_DURATION=30,
    # should lead to delays of 0.5, 1, 2, 4, 8, 16, 32 seconds
    DEFAULT_RETRY_BACKOFF_FACTOR=1,
    # system CA certificates path, default for RHEL variants
    REQUESTS_CA_BUNDLE="/etc/ssl/certs/ca-bundle.crt",
    # Testing Farm sanity test,
    TESTING_FARM_TESTS_GIT_URL="https://gitlab.com/testing-farm/tests",
    TESTING_FARM_SANITY_PLAN="/testing-farm/sanity",
    PUBLIC_IP_CHECKER_URL="https://ipv4.icanhazip.com",
    # number or tries for resolving localhost public IP, useful if the user has multiple IPs
    PUBLIC_IP_RESOLVE_TRIES=1,
)
