# BUMS 

## Introduction

BUMS—Bonner sphere Unfolding Made Simple: an HTML based multisphere neutron spectrometer unfolding package. 

Originally BUMS Perl coding by Jeremy Sweezy (Georgia Tech) in 2000. 
Additions by Pete Exline (Georiga Tech). 
Docker container by Jeremy Sweezy (LANL) in April 2025, jsweezy@lanl.gov.
Python modernization coding by Angel Mercado (Georgia Tech) and Lianna Arnold (Georgia Tech) in August 2025, amercado35@gatech.edu and larnold34@gatech.edu

Original article:
Sweezy, J., Hertel, N., & Veinot, K. (2002). 
BUMS—Bonner sphere Unfolding Made Simple: an HTML based multisphere neutron spectrometer unfolding package. 
Nucl. Instrum. Methods Phys. Res. A
476(1), 263–269. 
https://doi.org/10.1016/S0168-9002(01)01466-8


## Code Acknowledgements

Contains MAXED Fortran coding by Marcel Reginatto (mreg@eml.doe.gov) and Paul Goldhagen
(goldhagn@eml.doe.gov).   
- https://www.wipp.energy.gov/namp/emllegacy/reports/eml595.pdf   
- https://doi.org/10.1016/S0168-9002(01)01439-5   
- https://journals.lww.com/health-physics/abstract/1999/11000/maxed,_a_computer_code_for_maximum_entropy.12.aspx  

MAXED contains SAND-II from Sandia National Laboratory by Patrick Griffin, Jake Kelly, and Jason VanDenburg. https://doi.org/10.2172/10149711

The FORTRAN for BUNKI-UT is also included.  BUNKI-UT is a modification of BUNKI by Suzanne Peterson in March 1986 at the University of Texas, Austin. 

BUNKI was originally programmed at the Navel Research Laboratory in July, 1983 by Kimberly A. Lowry and Tommy L. Johnson. https://doi.org/10.1097/00004032-198410000-00006.  The listing for BUNKI is provided in:
https://apps.dtic.mil/sti/tr/pdf/ADA142475.pdf


## Building the Docker Image

Create the docker image - just do this once. Works for both the legacy and modern versions of BUMS.

`docker build -t bums-server .`

## Starting a Docker container

Start an instance and mount your bums repo as /usr/lib/cgi-bin (use your own path, not `/Users/jsweezy/git_repos/bums/`)

`docker run -it --rm   -v /Users/jsweezy/git_repos/bums/:/usr/lib/cgi-bin   -p 8080:80   bums-server   apachectl -D FOREGROUND`

## Running BUMS on web page

For the legacy version of BUMS, point your browser to: http://localhost:8080/cgi-bin/notezy.cgi

For the modern version of BUMS, point your browser to: http://localhost:8080/cgi-bin/web.cgi

## Running BUMS on command window

In order to run the legacy version from the command window, the user will need to enter the docker container. You will need to get the hash of the running docker container:

`docker ps`

You will see output like:
```
CONTAINER ID   IMAGE         COMMAND                  CREATED             STATUS             PORTS                  NAMES
b329bb59ef76   bums-server   "apachectl -D FOREGR…"   About an hour ago   Up About an hour   0.0.0.0:8080->80/tcp   romantic_ritchie
```

To start and interactive bash shel within the running container:

`docker exec -it b329bb59ef76 bash`

You will then see that you are in a bash shell within the container:

```
root@b329bb59ef76:/usr/lib/cgi-bin# 
```

To run BUMS within the docker contianer:
`./notezy_cli.pl /path/to/input /path/to/output`


In order to run the modern version of BUMS from the command window, point your system to the BUMS directory. 

`cd /Users/jsweezy/git_repos/bums/`

To run BUMS from the command window:
`python -m bums2.driver -i \path\to\input -o \path\to\output`


## Debugging errors

If you need to read errors from the server, start another shell.  You will need to get the hash of the running docker container:

`docker ps`

You will see output like:
```
CONTAINER ID   IMAGE         COMMAND                  CREATED             STATUS             PORTS                  NAMES
b329bb59ef76   bums-server   "apachectl -D FOREGR…"   About an hour ago   Up About an hour   0.0.0.0:8080->80/tcp   romantic_ritchie
```

To start and interactive bash shell within the running docker container:

`docker exec -it b329bb59ef76 bash`

You will then see that you are in a bash shell within the container:

```
root@b329bb59ef76:/usr/lib/cgi-bin# 
```

Then read the last entries in the Apache2 log to deduce the problem:

`tail -n 50 /var/log/apache2/error.log`


**********

Previous users of web based BUMS:

| Institution                                               | Country     |
|:----------------------------------------------------------|:------------|
| Agentina Nuclear Regulator (Autoridad Regulatoria Nuclear)         | Argentina   |
| ----                                                      | Canada      |
| ----                                                      | China       |
| Indian Institute of Technology                            | India       |
| Instituto Tecnológico de Estudios Superiores de Monterrey | Mexico      |
| Universidad Autónoma de San Luis Potosí                   | Mexico      |
| Korea Institute of Science and Technology                 | South Korea |
| Korea Institute of Science and Technology Information     | South Korea |
| Universidad Politécnica de Madrid                         | Spain       |
| Berkeley Lab                                              | USA         |
| Duke Energy Carolinas                                     | USA         |
| Emory University                                          | USA         |
| Georgia Institute of Technology                           | USA         |
| Idaho National Laboratory                                 | USA         |
| Los Alamos National Laboratory                            | USA         |
| National Institute of Standards and Technology            | USA         |
| Oak Ridge National Laboratory                             | USA         |
| Parsons Corporation                                       | USA         |
| Sandia National Laboratories                              | USA         |
| University of Tennessee                                   | USA         |
| Y-12 National Security Complex                            | USA         |

## References

@article{sweezy2002bums,
  title={BUMS—Bonner sphere Unfolding Made Simple: an HTML based multisphere neutron spectrometer unfolding package},
  author={Sweezy, Jeremy and Hertel, Nolan and Veinot, Ken},
  journal={Nucl. Instrum. Methods Phys. Res. A},
  volume={476},
  number={1},
  pages={263--269},
  year={2002},
  doi={10.1016/S0168-9002(01)01466-8},
  publisher={Elsevier}
}
