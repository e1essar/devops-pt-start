FROM postgres:15

COPY init.sql /docker-entrypoint-initdb.d/

ENV DB_USER=postgres
ENV DB_PASSWORD=Qq12345
ENV DB_DB=db_bot

CMD ["postgres"]