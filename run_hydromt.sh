#!/usr/bin/zsh

set -e

size=$1
data_catalog=$2

if [ -z "$size" ]
then
      size=small
elif [ "$size" != "small" ] && [ "$size" != "large" ]
then
    echo "Invalid size: $size"
    exit 1
fi

if [ "$size" = "small" ]
then
    region='{"subbasin": [9.666, 0.4476], "uparea": 100}'
else
    region='{"basin": [4.099565785808807, 51.97582874463458], "strord": 5}'
fi

if [ -z "$data_catalog" ]
then
    data_catalog=data_catalogs/deltares-data-curated.yaml
fi

hydromt build wflow -vv "./wflow_$size" -i wflow-build.ini -r "$region" -d $data_catalog 2>&1 > /dev/null
