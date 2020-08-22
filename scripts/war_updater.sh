#!/bin/sh

source $1/$2/bin/activate
cd $1
$3
deactivate
cd