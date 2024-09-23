# URL of the InfluxDB server
url = "http://hime02:8086"

# Name of the organization you want to write data to.
org = "HIME"

# Name of the bucket you want to write data to.
bucket = "HIME"

# The default time interval in which data is submitted to InfluxDB,
# given in seconds.
# Enter a negative number to disable data submission completely.
# Non-negative numbers smaller than 5 will be set to 5 automatically.
writeTime = 60
