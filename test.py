import CloudFlare

cf = CloudFlare.CloudFlare(email='robertahmetzyanov1@gmail.com', key='02eade823590ee28043c6b8045e93cdefb8f3')

print(cf.zones.get())
