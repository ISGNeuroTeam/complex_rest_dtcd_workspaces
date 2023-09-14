FROM python:3.9.7
ENV PYTHONUNBUFFERED=1

ENV DATABASE=postgres
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres
ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV REST_CONF=/complex_rest/docs/docker_dev/complex_rest/rest.conf
ENV PYTHONPATH=/complex_rest/complex_rest
ENV dtcd_workspaces_conf=/complex_rest/complex_rest/dtcd_workspaces.conf

RUN mkdir /complex_rest

RUN git clone -b feature/keycloak_integration https://github.com/ISGNeuroTeam/complex_rest.git

RUN chmod -R 0777 /complex_rest

ADD ./docs/docker/dtcd_workspaces.conf /complex_rest/complex_rest/dtcd_workspaces.conf
ADD ./docs/docker/entrypoint.sh /complex_rest/entrypoint.sh

WORKDIR /complex_rest

RUN pip install --no-cache-dir  -r requirements.txt


ENTRYPOINT ["/complex_rest/entrypoint.sh"]
CMD ["python /complex_rest/complex_rest/manage.py runserver [::]:8080"]
EXPOSE 8080