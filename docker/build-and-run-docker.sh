### "make-container"
docker build -t cameronneylon/plos-journals . && \
	docker run -t -i \
    -v "/Users/cameronneylon/Google Drive/prog/affiliations":/home/work/affiliations cameronneylon/plos-journals /bin/bash