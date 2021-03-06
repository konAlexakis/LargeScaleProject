from pyspark.sql.types import DoubleType

from helpers import init_spark, haversine, elapsed_time, find_max


class Q2(object):
    def __init__(self):
        self.spark, self.sc = init_spark()

    def sql_api(self, trip_data, vendors):
        """This function is used to execute Q1 using SparkSQL"""

        trip_data.registerTempTable("trips")
        vendors.registerTempTable("vendors")

        self.spark.udf.register('elapsed_time', elapsed_time)
        self.spark.udf.register('haversine', haversine)

        vendor_trips = self.spark.sql(
            "SELECT vendors._c1 as vendor_id, elapsed_time(trips._c1,trips._c2) as duration, haversine(cast(_c3 as float), cast(_c4 as float), cast(_c5 as float), cast(_c6 as float)) as distance FROM trips INNER JOIN vendors ON trips._c0=vendors._c0 WHERE trips._c3!='0' AND trips._c4!='0' AND trips._c5!='0' AND trips._c6!='0'")
        vendor_trips.registerTempTable("vendor_trips")

        groups = self.spark.sql("SELECT vendor_id, MAX(distance) as max_distance FROM vendor_trips GROUP BY vendor_id")
        grp_rdd = groups.rdd.collect()

        result = self.spark.sql(
            "SELECT * FROM vendor_trips WHERE vendor_id={} AND distance={} OR vendor_id={} AND distance={}".
            format(grp_rdd[0]['vendor_id'], grp_rdd[0]['max_distance'], grp_rdd[1]['vendor_id'],
                   grp_rdd[1]['max_distance'])
            )
        result.show()

    def mr_api(self, trip_data,vendors):

        trip_data = trip_data.map(lambda x : (x.split(",")[0],x.split(",")[1],x.split(",")[2],float(x.split(",")[3]),float(x.split(",")[4]),float(x.split(",")[5]),float(x.split(",")[6])))

        filtered_trip_data=trip_data.filter(lambda x : x[3]!=0 and x[4]!=0 and x[5]!=0 and x[6]!=0). \
                                    map(lambda x : (x[0],(elapsed_time(x[1],x[2]),haversine(x[3], x[4], x[5], x[6]))))

        vendors = vendors.map(lambda x : (x.split(",")[0], x.split(",")[1]))


        result = filtered_trip_data.join(vendors). \
                                    map(lambda x : (x[1][1], [x[1][0][0],x[1][0][1]])). \
                                    reduceByKey(lambda x,y: find_max(x,y)). \
                                    map(lambda x : (x[0],x[1][0],x[1][1]))


        for i in result.collect():
            print(i)
