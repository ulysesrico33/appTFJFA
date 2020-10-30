import json
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
import os

pathToHere=os.getcwd()
def main():
    #Connect to Cassandra
    objCC=CassandraConnection()
    auth_provider = PlainTextAuthProvider(objCC.cc_user,objCC.cc_pwd)
    cloud_config= {
        'secure_connect_bundle': pathToHere+'\\secure-connect-dbquart.zip'
    }              
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.default_timeout=70
        
    row=''
    print('Getting all sent...')
       
    querySt="select id from thesis.tbcourtdecisioncjf"   
        
    count=0
    statement = SimpleStatement(querySt, fetch_size=1000)
    for row in session.execute(statement):
        count=count+1
        
    print('Count',str(count))   
    cluster.shutdown() 

   
class CassandraConnection():
    cc_user='quartadmin'
    cc_keyspace='thesis'
    cc_pwd='P@ssw0rd33'
    cc_databaseID='9de16523-0e36-4ff0-b388-44e8d0b1581f'

if __name__=='__main__':
    main()    
        

