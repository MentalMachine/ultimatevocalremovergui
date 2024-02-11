# Makefile
# make docker

APP_VERSION=$(shell git describe --always --dirty)

docker:
	docker build . -t org.opo/ultimate-vocal-remover-cli:${APP_VERSION} -t org.opo/ultimate-vocal-remover-cli:latest