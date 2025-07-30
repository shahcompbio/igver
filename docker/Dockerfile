# docker build -t sahuno/igver:latest .
# docker push sahuno/igver:latest

# setup: using archlinux because it was the only distro where I could find --auto-display
FROM archlinux:latest

RUN pacman -Syu --noconfirm  xorg-server-xvfb python wget pacman jdk-openjdk unzip git libxtst

# get IGV 2.19.5
RUN wget https://data.broadinstitute.org/igv/projects/downloads/2.19/IGV_2.19.5.zip && \
    unzip IGV_2.19.5.zip -d /opt && \
	rm IGV_2.19.5.zip
RUN mkdir -p /opt/IGV_2.19.5/genomes 

WORKDIR /opt/IGV_2.19.5

# font config
RUN pacman -Syu --noconfirm  gnu-free-fonts opendesktop-fonts ttf-dejavu fontconfig
RUN fc-cache -f -v

# install python packages
RUN pacman -Syu --noconfirm python-pip python-yaml python-matplotlib python-pillow

# download igver
RUN git clone https://github.com/sahuno/igver.git /opt/igver

# install igver and its dependencies (using --break-system-packages for Arch Linux)
RUN cd /opt/igver && pip install --break-system-packages -e .

# create wrapper script for backward compatibility
RUN echo '#!/usr/bin/env python' > /opt/igver/igver.py && \
    echo 'from igver.cli import main' >> /opt/igver/igver.py && \
    echo 'if __name__ == "__main__":' >> /opt/igver/igver.py && \
    echo '    main()' >> /opt/igver/igver.py && \
    chmod +x /opt/igver/igver.py

ENV PATH="$PATH:/opt/igver:/opt/IGV_2.19.5"

# add genomes (from https://github.com/igvteam/igv/wiki/Downloading-Hosted-Genomes-for-Offline-Use/26e9731ef36889a974b0b6fa94fce7b36d67543e#hosted-genome-list)
ADD json/ASM294v2.json /opt/IGV_2.19.5/genomes/ASM294v2.json
ADD json/ASM985889v3.json /opt/IGV_2.19.5/genomes/ASM985889v3.json
ADD json/bosTau8.json /opt/IGV_2.19.5/genomes/bosTau8.json
ADD json/bosTau9.json /opt/IGV_2.19.5/genomes/bosTau9.json
ADD json/canFam3.json /opt/IGV_2.19.5/genomes/canFam3.json
ADD json/canFam5.json /opt/IGV_2.19.5/genomes/canFam5.json
ADD json/ce11.json /opt/IGV_2.19.5/genomes/ce11.json
ADD json/danRer10.json /opt/IGV_2.19.5/genomes/danRer10.json
ADD json/danRer11.json /opt/IGV_2.19.5/genomes/danRer11.json
ADD json/dm3.json /opt/IGV_2.19.5/genomes/dm3.json
ADD json/dm6.json /opt/IGV_2.19.5/genomes/dm6.json
ADD json/dmel_r5.9.json /opt/IGV_2.19.5/genomes/dmel_r5.9.json
ADD json/galGal6.json /opt/IGV_2.19.5/genomes/galGal6.json
ADD json/gorGor4.json /opt/IGV_2.19.5/genomes/gorGor4.json
ADD json/gorGor6.json /opt/IGV_2.19.5/genomes/gorGor6.json
ADD json/hg18.json /opt/IGV_2.19.5/genomes/hg18.json
ADD json/hg19.json /opt/IGV_2.19.5/genomes/hg19.json
ADD json/hg38.json /opt/IGV_2.19.5/genomes/hg38.json
ADD json/hg38_1kg.json /opt/IGV_2.19.5/genomes/hg38_1kg.json
ADD json/macFas5.json /opt/IGV_2.19.5/genomes/macFas5.json
ADD json/mm10.json /opt/IGV_2.19.5/genomes/mm10.json
ADD json/mm9.json /opt/IGV_2.19.5/genomes/mm9.json
ADD json/panPan2.json /opt/IGV_2.19.5/genomes/panPan2.json
ADD json/panTro4.json /opt/IGV_2.19.5/genomes/panTro4.json
ADD json/rn6.json /opt/IGV_2.19.5/genomes/rn6.json
ADD json/sacCer3.json /opt/IGV_2.19.5/genomes/sacCer3.json
ADD json/tair10.json /opt/IGV_2.19.5/genomes/tair10.json

# custom genome (hs1 from https://s3.amazonaws.com/igv.org.genomes/genomes.json)
ADD json/hs1.json /opt/IGV_2.19.5/genomes/hs1.json

# New genomes for mm39
ADD json/mm39.json /opt/IGV_2.19.5/genomes/mm39.json

RUN chmod -R 777 /opt