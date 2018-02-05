FROM python:3
RUN mkdir -p /app/bl3bot
ADD . /app/bl3bot
WORKDIR /app/bl3bot
CMD ["make -j2"]
