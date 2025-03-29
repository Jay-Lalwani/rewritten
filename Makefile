all: auth build tag push

auth:
	aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/t7k1y3c2

build:
	docker buildx build --platform linux/amd64 -t rewritten .

tag:
	docker tag rewritten:latest public.ecr.aws/t7k1y3c2/rewritten:latest

push:
	docker push public.ecr.aws/t7k1y3c2/rewritten:latest

run:
	docker run -p 3000:3000 rewritten:latest
