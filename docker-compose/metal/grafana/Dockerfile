FROM grafana/grafana


COPY /datasource.yml /etc/grafana/provisioning/datasources/
COPY /dashboards.yml /etc/grafana/provisioning/dashboards/
COPY /dashboards/* /var/lib/grafana/dashboards/

