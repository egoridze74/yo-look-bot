run:
	docker run -it -d --env-file .env --restart=unless-stopped --name tg_bot bot_image
stop:
	docker stop tg_bot
attach:
	docker attach tg_bot
dell:
	docker rm tg_bot