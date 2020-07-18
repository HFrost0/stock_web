FROM centos
COPY c.txt /usr/local/cincontainer.txt
ADD jdk-adfadfadfadfad.tar /usr/local/
ADD apache-adfadfadfadfad.tar /usr/local/
RUN yum -y install vim
ENV MYPATH /usr/local
WORKDIR $MYPATH



