app_name = "nlp-pdf:latest"

help:
	@echo ''
	@echo 'NLP PDF taxonomy and NSC extraction Docker build'
	@echo '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
	@echo ''

build:
	echo "copying models ..." && \
	cp ../nlp_pdf/models/*.pkl . && \
	docker build -t $(app_name) . && \
	rm *.pkl
run:
	docker run -i \
		-t \
		--rm \
		-p 8050:8050 \
		$(app_name)
stop:
	@echo "Killing $(app_name) ..."
	@docker ps | grep $(app_name) | awk '{print $1}' | xargs docker stop
