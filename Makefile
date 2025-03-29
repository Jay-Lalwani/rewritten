all: auth build tag push

auth:
	AWS_PROIFLE=personal aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/t7k1y3c2

build-am64:
	docker buildx build --platform linux/amd64 -t rewritten .

build:
	docker build -t rewritten .

tag:
	docker tag rewritten:latest public.ecr.aws/t7k1y3c2/rewritten:latest

push:
	docker push public.ecr.aws/t7k1y3c2/rewritten:latest

run:
	docker run -p 3000:3000 rewritten:latest
