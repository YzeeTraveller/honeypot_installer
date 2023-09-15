# This file is part of the dionaea honeypot
#
# SPDX-FileCopyrightText: 2018 PhiBo (DinoTools)
#
# SPDX-License-Identifier: GPL-2.0-or-later

include(InstallRequiredSystemLibraries)
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Dionaea is meant to be a nepenthes successor, embedding python as scripting language, using libemu to detect shellcodes, supporting ipv6 and tls.")
set(CPACK_PACKAGE_VENDOR "dionaea team")
set(CPACK_PACKAGE_DESCRIPTION_FILE "${CMAKE_CURRENT_SOURCE_DIR}/README.md")
set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE")
set(CPACK_PACKAGE_VERSION_MAJOR "${PROJECT_VERSION_MAJOR}")
set(CPACK_PACKAGE_VERSION_MINOR "${PROJECT_VERSION_MINOR}")
set(CPACK_PACKAGE_VERSION_PATCH "${PROJECT_VERSION_PATCH}")
set(CPACK_PACKAGE_INSTALL_DIRECTORY "dionaea")
set(CPACK_SOURCE_PACKAGE_FILE_NAME "dionaea-${PACKAGE_VERSION}")
set(CPACK_SOURCE_GENERATOR "TGZ")
set(CPACK_GENERATOR "TGZ")
set(CPACK_STRIP_FILES "bin/dionaea")
set(CPACK_SOURCE_IGNORE_FILES "/.tx/" "/CVS/" "/.svn/" "/.git/" "/.github/" "/.bzr/" "builds/" "installers/" "util/spout2" "/CMakeLists.txt.user$" "\\\\.bzrignore$" "\\\\.gitignore$" "\\\\.clang-format$" "\\\\.yml$" "~$" "\\\\.swp$" "\\\\.#" "/#")
set(CPACK_RPM_PACKAGE_LICENSE "GPLv2+")
set(CPACK_RPM_PACKAGE_GROUP "System")
set(CPACK_RPM_PACKAGE_URL "")
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "${CPACK_PACKAGE_VENDOR} <>")
set(CPACK_DEBIAN_PACKAGE_SECTION "science")
set(CPACK_DEBIAN_PACKAGE_VERSION "${VERSION}+deb1")
set(CPACK_DEBIAN_PACKAGE_HOMEPAGE "${CPACK_RPM_PACKAGE_URL}")
set(CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON)
include(CPack)
