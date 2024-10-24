FROM eye-base:latest
USER root
ENV DEBIAN_FRONTEND=noninteractive

EXPOSE 8000
EXPOSE 8080

WORKDIR /eyes-classification

COPY . .

# CMD ./start.sh
ENTRYPOINT ["/bin/bash", "start.sh"]
