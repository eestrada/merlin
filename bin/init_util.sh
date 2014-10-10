#!/bin/bash

APP_DIR="$1"
CUR_DIR="$(pwd)"
if [ ! "${MFS}/bin" -ef "${APP_DIR}" ]; then
	if [ -e "${APP_DIR}/../merlin_setup" ]; then
		cd "${APP_DIR}/.." && source merlin_setup && cd "${CUR_DIR}"
	fi
elif [ ! "${MFS}/merlin/sbin" -ef "${APP_DIR}" ]; then
	if [ -e "${APP_DIR}/../../merlin_setup" ]; then
		cd "${APP_DIR}/../.." && source merlin_setup && cd "${CUR_DIR}"
	fi
fi
