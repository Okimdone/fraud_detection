# pyspark --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1
# spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1 /app/src/MyPythonScript.py 

# from pyspark.sql import SQLContext
import os
from pyspark import SparkContext, SparkConf
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import IntegerType, StringType, StructType, StructField, DoubleType 
from elephas.utils.rdd_utils import to_simple_rdd
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import activations
from tensorflow.keras import initializers
from elephas.spark_model import SparkModel
import numpy as np

# DEFINITIONS : 

KAFKA_TOPIC = "transactions"
KAFKA_SERVER = "kafka_broker:9092"
MODEL_SAVING_PATH = "/models/fraud_detector/{}"

sch = StructType([
    StructField("schema", StringType()),
    StructField("payload", StringType())
])
sch2 = StructType([
    StructField("Time", StringType()),
    StructField("V1", StringType()),
    StructField("V2", StringType()),
    StructField("V3", StringType()),
    StructField("V4", StringType()),
    StructField("V5", StringType()),
    StructField("V6", StringType()),
    StructField("V7", StringType()),
    StructField("V8", StringType()),
    StructField("V9", StringType()),
    StructField("V10", StringType()),
    StructField("V11", StringType()),
    StructField("V12", StringType()),
    StructField("V13", StringType()),
    StructField("V14", StringType()),
    StructField("V15", StringType()),
    StructField("V16", StringType()),
    StructField("V17", StringType()),
    StructField("V18", StringType()),
    StructField("V19", StringType()),
    StructField("V20", StringType()),
    StructField("V21", StringType()),
    StructField("V22", StringType()),
    StructField("V23", StringType()),
    StructField("V24", StringType()),
    StructField("V25", StringType()),
    StructField("V26", StringType()),
    StructField("V27", StringType()),
    StructField("V28", StringType()),
    StructField("Amount", StringType()),
    StructField("Class", StringType())
])

def  clean_DF(batchDF):
    y1  = batchDF.select(batchDF.value.cast('string'))
    y2 = y1.withColumn("value",from_json(col("value"),sch))
    y3 = y2.withColumn('value', y2.value.payload)
    y4 = y3.withColumn('value', from_json("value",sch2))
    y5 = y4.select(col("value.*"))
    y6 = y5.select(y5.Time.cast(DoubleType()), y5.V1.cast(DoubleType()), y5.V2.cast(DoubleType()), y5.V3.cast(DoubleType()), 
            y5.V4.cast(DoubleType()), y5.V5.cast(DoubleType()), y5.V6.cast(DoubleType()),y5.V7.cast(DoubleType()), 
            y5.V8.cast(DoubleType()), y5.V9.cast(DoubleType()), y5.V10.cast(DoubleType()), y5.V11.cast(DoubleType()), 
            y5.V12.cast(DoubleType()), y5.V13.cast(DoubleType()), y5.V14.cast(DoubleType()), y5.V15.cast(DoubleType()), 
            y5.V16.cast(DoubleType()), y5.V17.cast(DoubleType()), y5.V18.cast(DoubleType()), y5.V19.cast(DoubleType()), 
            y5.V20.cast(DoubleType()), y5.V21.cast(DoubleType()), y5.V22.cast(DoubleType()), y5.V23.cast(DoubleType()), 
            y5.V24.cast(DoubleType()), y5.V25.cast(DoubleType()), y5.V26.cast(DoubleType()), y5.V27.cast(DoubleType()), 
            y5.V28.cast(DoubleType()), y5.Amount.cast(DoubleType()), y5.Class.cast(DoubleType()))
    y7 = y6.withColumnRenamed('Class', 'Fraud')
    y =y7.withColumn('Normal', -y7.Fraud+1)
    return y


# Session and Extracting the data
conf = SparkConf().setAppName('Fraud_Detection_Training_App').setMaster('local[8]')
sc = SparkContext(conf=conf)

# creating an instance of SparkSession
spark = SparkSession \
    .builder \
    .appName("My spark Streaming process") \
    .getOrCreate()

# Subscribe to 1 topic
df = spark \
    .read \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_SERVER) \
    .option("subscribe", KAFKA_TOPIC) \
    .load()

# DATA TRANSFORMATION 
df = clean_DF((df))
# query = df.writeStream.trigger(processingTime='2 seconds').foreachBatch(func).outputMode("update").start()

features = ['Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9',
       'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18',
       'V19', 'V20', 'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27',
       'V28', 'Amount']
targets = ['Normal', 'Fraud']
# Number of nodes in each layer.
input_nodes = len(features)
hidden_nodes1 = 20
hidden_nodes2 = 20
hidden_nodes3 = 20

# MODEL DEFINITION
x = keras.Input(shape=input_nodes)
y1 = layers.Dense(
    hidden_nodes1, 
    name='layer_1',
    activation = activations.sigmoid, 
    kernel_initializer = initializers.RandomNormal(stddev=0.01), 
    bias_initializer = initializers.Zeros())
y2 = layers.Dense(
    hidden_nodes2,
    name='layer_2',
    activation = activations.sigmoid, 
    kernel_initializer = initializers.RandomNormal(stddev=0.01), 
    bias_initializer = initializers.Zeros())
y3 = layers.Dense(
    hidden_nodes3, 
    name='layer_3',
   activation = activations.sigmoid, 
   kernel_initializer = initializers.RandomNormal(stddev=0.01), 
   bias_initializer = initializers.Zeros())
y5 = layers.Dense(
    2, 
    name="OUTPUT",
    activation = activations.softmax, 
    kernel_initializer = initializers.RandomNormal(stddev=0.01), 
    bias_initializer = initializers.Zeros())
y = y5
model = keras.Sequential([x, y1, y2, y3, y])

# MODEL COMPILATION 
training_epochs = 1000
batch_size = 2048
learning_rate = 0.05

model.compile(
    loss = keras.losses.categorical_crossentropy,
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate),
    metrics=["accuracy", "Recall"] 
)
model.summary()

# TRAINING ON THE DATA OVER A CLUSTER
x_train = df.select(features)
y_train = df.select(targets)

spark_model = SparkModel(model, frequency='epoch', mode='asynchronous')
rdd = to_simple_rdd(sc, np.array(x_train.collect()), np.array(y_train.collect()))
spark_model.fit(rdd, epochs=training_epochs, batch_size=batch_size, verbose=1, validation_split=0.1)

# SAVING THE MODEL
nextModelVersion = int(max(os.listdir('/models/fraud_detector'))) + 1
spark_model.save(MODEL_SAVING_PATH.format(nextModelVersion))