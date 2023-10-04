find "*.log" logs -exec awk -v file={} '/=>/{if($7!="0B"){print file "," $2 "," $7}}' {} \;
