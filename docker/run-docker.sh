### "make-container"
docker build -t oacensus/development . && \
    docker run -t -i \
    -v `pwd`/../affiliations:/home/work/affiliations \
    oacensus/development /bin/bash