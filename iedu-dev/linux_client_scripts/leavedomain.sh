#!/bin/bash

echo "; ; ; ; ; ; ; ; ; ;" | net ads leave -U user%password

rm -f /usr/local/etc/dom_joined
