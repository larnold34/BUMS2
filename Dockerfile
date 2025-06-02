# Use a base Linux image that includes Perl 5
FROM debian:12.10-slim

# Install necessary packages including text editors
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    perl \
    libcgi-pm-perl \
    libchart-perl \
    python3 \
    build-essential \
    gfortran \
    apache2 \
    apache2-bin \
    vim \
    vim-gtk3 \
    gnuplot \
    nano && \
    rm -rf /var/lib/apt/lists/*

 RUN apt-get update && apt-get install -y --no-install-recommends \ 
     curl \ 
     wget && \
     rm -rf /var/lib/apt/lists/*

 RUN apt-get update && apt-get install -y --no-install-recommends \ 
     libwww-perl \
     libmodule-build-perl \
     ca-certificates && \
     rm -rf /var/lib/apt/lists/*

 RUN apt-get update && apt-get install -y --no-install-recommends \ 
     gdb-minimal && \ 
     rm -rf /var/lib/apt/lists/*

# Enable CGI module in Apache
RUN a2enmod cgi

# Suppress ServerName warning
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# Helps Perl see the Math folder, fixes the interval search issue
COPY ./MATH /usr/local/lib/site_perl/Math
ENV PERL5LIB=/usr/local/lib/site_perl
RUN echo "PERL5LIB=/usr/local/lib/site_perl" >>/etc/apache2/envvars


# Configure Apache to execute CGI scripts from /usr/local/apache2/cgi-bin
RUN chmod 755 /usr/lib/cgi-bin

# Configure Apache to handle .pl and .py files as CGI scripts
RUN echo "ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/" >>  /etc/apache2/sites-available/000-default.conf
RUN echo "<Directory /usr/lib/cgi-bin>" >> /etc/apache2/sites-available/000-default.conf
RUN echo "    AllowOverride None" >> /etc/apache2/sites-available/000-default.conf
RUN echo "    Options +ExecCGI" >> /etc/apache2/sites-available/000-default.conf
RUN echo "    AddHandler cgi-script .cgi .pl .py" >> /etc/apache2/sites-available/000-default.conf
RUN echo "    Require all granted" >> /etc/apache2/sites-available/000-default.conf
RUN echo "</Directory>" >> /etc/apache2/sites-available/000-default.conf

# Enable the default site configuration
RUN a2ensite 000-default.conf

# Expose port 80
EXPOSE 80

# Set the working directory
WORKDIR /usr/lib/cgi-bin

RUN mkdir -p /var/www/html/tmp/notezy && \
    chmod 0755 /var/www/html/tmp && \
    chmod 0755 /var/www/html/tmp/notezy && \
    chown www-data:www-data /var/www/html/tmp/notezy  # Assuming www-data is the Apache user

# Update CA certificates explicitly
RUN update-ca-certificates

#RUN yes | perl -MCPAN -e 'CPAN::Shell->install(Bundle::CPAN)'
RUN perl -MCPAN -e 'install Chart::Graph'

# Pre-configure CPAN to skip tests
RUN perl -MCPAN -e 'CPAN::Config->{test} = [qw(none)]'

# Install Chart::Graph
RUN yes none | perl -MCPAN -e 'install Chart::Graph'

#Install Math::Fortran
RUN perl -MCPAN -e 'install Math::Fortran'

# --- Compile Fortran Code ---
# Copy the Fortran source code from the build context temporarily
RUN mkdir -p /tmp/BUMS/
COPY ./FORTRAN/BUNKI-UT/bunkiut.f /tmp/BUMS/
COPY ./FORTRAN/SAND2/sand.for /tmp/BUMS/
COPY ./FORTRAN/MAXED/maxed.for /tmp/BUMS/

# Compile the Fortran code using gfortran, placing executables in /usr/local/bin
RUN gfortran /tmp/BUMS/maxed.for -o /usr/local/bin/maxed -ffixed-form -fdec -fdefault-real-8 -std=legacy -g3 -O0 -fbacktrace 
RUN gfortran /tmp/BUMS/bunkiut.f -o /usr/local/bin/bunkiut -ffixed-form -fdec -fdefault-real-8 -std=legacy -g3 -O0 -fbacktrace  
RUN gfortran /tmp/BUMS/sand.for -o /usr/local/bin/sand2 -ffixed-form -fdec -fdefault-real-8 -std=legacy -g3 -O0 -fbacktrace 
RUN chmod +x /usr/local/bin/bunkiut /usr/local/bin/maxed /usr/local/bin/sand2 
#RUN rm /tmp/BUMS/*
# --- End Fortran Compilation ---

# Disable default CGI config to avoid ScriptAlias overlap
RUN a2disconf serve-cgi-bin

# Start Apache in the foreground
CMD ["apache2ctl", "-D", "FOREGROUND"]
