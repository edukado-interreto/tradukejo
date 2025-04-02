dc := docker compose
user_id := $(shell id -u)
group_id := $(shell id -g)

all: run

run:
	USER_ID=$(user_id) GROUP_ID=$(group_id) $(dc) up
