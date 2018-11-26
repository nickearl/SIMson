# SIMson
A python-based utility to generate dummy analytics data using the Segment python library

This is a python script intended to be run as a Docker container.  It generates simulated user sessions to pass dummy analytics data for testing purposes
using the Segment python library.

# Usage:

You will need a data.db file (see 'Dummy data DB structure' section below).  Save this in a dir somewhere.

**Using Docker Hub**
1) Grab the image from Docker Hub

  `<>`
 
2) Run the image, passing in a Segment write key and mount a dir containing a sqlite3 database named "data.db" containing dummy data to send

  `docker run -it --rm -e "WRITE_KEY=<your write key>" -v <your dir containing data.db>:/data simson`

**Build from source**
1. Pull this repository
2. Either replace "/db/segment_dummy_schema.db" with your data.db file OR when running container, mount a dir containing data.db as in Docker Hub instructions
3. From within repo root, build the image
  `docker build -t simson .`
4. Run the image

  `docker run -it --rm -e "WRITE_KEY=<your write key>" simson #(if you replaced /db/segment_dummy_schema.db)`
  OR
  `docker run -it --rm -e "WRITE_KEY=<your write key>" -v <your dir containing data.db>:/data simson`

# Config file options:

The config file (/config.yml) has the following options:

**Segment settings**
```
segment:
  writeKey: key_12345 # This is a dummy write key- pass your own write key as an env variable in the "docker run" command above
  charlesCertPath: charles-ssl-proxying-certificate.pem # No need to modify; this is used if proxying SSL via Charles
```
**Database settings**
```
db:
  path: db/segment_dummy_schema.db # An example DB file- pass your own by replacing this file or mounting a path in the "docker run" command above
```
**Session settings**
```
session:
  #Set minimum number of pages/screens/events to send each session
  requestsMin: 1
  #Set maximum number of pages/screens/events to send each session
  requestsMax: 24
  #Set min number of seconds to wait between requests
  delayMin: 1
  #Set max number of seconds to wait between requests
  delayMax: 5
```
# Dummy data DB structure:

See /db/segment_dummy_schema.db for example file

The DB file must be in the following format:
* Tables:
  * "pages"
    * Requires first column 'id' INT as a primary key/id
    * Requires a second column 'name' that will represent the page name
    * Can contain any number of additional columns as property key names
    * Each record represents a single page or screen view request to be selected randomly
  * "event_names"
    * Requires first column 'id' INT as a primary key/id
    * Requires a second column 'event_name' that will represent track call names
    * Each track call to be fired must appear as a record in this table
  * "traits"
    * Requires first column 'id' INT as a primary key/id
    * Can contain any number of additional columns as trait key names (these are properties passed on every Segment request)

The DB file should then also include a table for each event (track call) to be fired, in this format:
 * Table name: <name of the event> (case sensitive) (use the event names set in "event_names" table)
 * Requires first column 'id' INT as a primary key/id
 * Can contain any number of additional columns as property key names specific to that event/track call

# Notes
For our implementations, on track calls we also include all properties from the last fired page/screen call.  This utility simulates this, 
but if this behavior is not desired, modify the relevent lines in the `segmentTrack` method to avoid pulling in a random set of page properties on each track event.
# More info:
Segment python library docs: https://segment.com/docs/sources/server/python/
