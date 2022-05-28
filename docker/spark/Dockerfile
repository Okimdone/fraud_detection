FROM docker.io/bitnami/spark:3

USER root
RUN chmod -R a+rwx /opt /bin

RUN pip install tensorflow
RUN pip install elephas
#COPY ./elephas-3.0.0.tar.gz /home/
#RUN tar -xvzf /home/elephas-3.0.0.tar.gz -C /home/
#RUN python /home/elephas-3.0.0/setup.py install

#ENTRYPOINT ["spark-submit", "--packages", "org.apache.spark:spark-streaming-kafka-0-8_2.11:2.3.0","Training_job.py"]
