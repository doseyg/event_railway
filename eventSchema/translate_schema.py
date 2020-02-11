import csv
 
mapping_file="EventSchemaMappings.csv"
output_file="result.txt"
#output_formats kv json logstash
output_format="logstash"
source_schema="PanOS:Traffic"
#Highest to lowest priority order of destination schemas
dest_schemas=("CEF","CFT_Schema","Unmapped")
on_fail="map_to_name"
on_fail="dont_map"
## copy or replace
logstash_action="copy"
 

mappings=""
 
with open(mapping_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row[source_schema]:
            src_field=row[source_schema].strip()
            dst_field="NULL"
            for schema in dest_schemas:
                if row[schema]:
                    dst_field=row[schema].strip()
                    continue
            if dst_field=="NULL":
                if on_fail=="map_to_name":
                    print("No mapping for "+ src_field +", mapped to self")
                    dst_field=src_field
                else:
                    print("No mapping for "+ src_field +", did not map")
                    continue
            if output_format == "json":
                mapping = '"'+dst_field+'":"'+src_field+'", '
                mappings = mappings + mapping
            if output_format == "kv":
                mapping = dst_field+'='+src_field+' '
                mappings = mappings + mapping
            if output_format == "logstash":
                mapping = logstash_action +' => {"'+src_field+'" => "'+dst_field+'" } \r\n'
                mappings = mappings + mapping
if output_format == "json":
    mappings = mappings.rstrip(", ")
    mappings = '{'+mappings+'}'  
    
print(mappings)
 
f = open(output_file, "w")
f.write(mappings)
f.close()
 
exit()
