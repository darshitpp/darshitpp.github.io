+++
title = "How to achieve a 50% reduction in Redis memory usage"
date = 2020-05-10T21:25:01+05:30
tags = ["redis", "java"]
categories = []
draft = false
+++

Yes, you read that right.

To give you some context, some time ago, our (my org's) Redis usage was un-tracked -- meaning we didn't know why our Redis memory was being occupied as much as it was. Our 2.5GB of Redis ElastiCache was almost close to being full, and if it somehow reached its limit, our system would start to fail. Though there were fallbacks in place, Redis could turn out to be a bottle-neck.

In this post, I would try to explain how we reduced the storage occupied by the data by more than 50%. This would also kind of be a step by step guide from the basics, so if you're just interested in how Redis is being used, just skip the and go to the Optimization section.

# Basic Setup

I would be using the latest version of Spring Boot from <https://start.spring.io>. Firstly, select our two of our main dependencies - `Spring Boot Web` and `Spring Data Reactive Redis`. 

You would find these in the `pom.xml` file when you download the starter project.

The `Spring Boot Web` is for building basic web applications with Spring Boot, whereas `Spring Data Reactive Redis` would be used for connecting and using Redis inside the application. At its core, the Redis dependency by default uses the [Lettuce](https://lettuce.io/) Redis client, and is supported by the latest versions of Spring Boot.

Note that I'm going to skip the installation of Redis, as there are other guides available for every operating system. You do need the Redis Server to be started for our application to work successfully.

After downloading the basic application, you'll need to extract and open it in your favourite IDE (my favourite one is IntelliJ IDEA).

In my case the project name is `redis-util`, and you'll find my "base packages" to be named `com.darshitpp.redis.redisutil`. This base package would have a class called `RedisUtilApplication`, which in my case has the following configuration.

```java
@SpringBootApplication
@ComponentScan(basePackages = {"com.darshitpp.redis.redisutil"})
public class RedisUtilApplication {

	public static void main(String[] args) {
		SpringApplication.run(RedisUtilApplication.class, args);
	}

}
```

I have manually added the `@ComponentScan` annotation to specify a top-level package name under where Spring should look for defined Beans/Configurations.

To connect to Redis, I create a configuration class called `LettuceRedisConfiguration`, under a new package named `configuration`(note that this should be under the `basePackages` path defined above.

You could define the configuration in the `RedisUtilApplication` class itself, but I want this to be as "production-ready" as possible. Thus, it's a good practice to separate out your different parts of application.

My configuration class is
```java
@Configuration
public class LettuceRedisConfiguration {

    @Bean
    public LettuceConnectionFactory redisConnectionFactory() {
        return new LettuceConnectionFactory(new RedisStandaloneConfiguration("localhost", 6379));
    }

}
```
It is a very simple class, which has the configuration of which URL to connect to for Redis. In my case, it is `localhost`, but in most production apps, it would be an external Redis server. Port `6379` is the default port on which the Redis server starts. This `Bean` would return us a "factory" of Redis connections. Think of this as something which would allow you to connect to Redis when required. 

At this point, my package structure looks like:
```txt
->src
  ->main
    ->java
      ->com.darshitpp.redis.redisutil
        ->configuration
```

Now that we know how to connect to a Redis server, we need to figure out what data we need to store in Redis. In our case, we would be storing `User` data. This is the "domain model" of our application (domain model could be translated to a table in a Database, but we don't have a table in our scenario). This `User` is stored in a package called `domain`.

The `User` would have three fields, namely, `firstName`, `lastName`, and `birthday`.

Before storing the objects in Redis, it is a good idea to identify *how* you will store the data so that it's efficient to fetch it back. What that means is Redis being a simple Key-Value store, you would need to identify the Key you would be storing the Value with. In our case, I am choosing `firstName` as the key. The data would be stored in a hash, so the `hashKey` that we select would be the `lastName` and the value mapped to the `hashKey` is the `User` object.

This is because Hashes in Redis have the following structure:

```txt
key1 --- hashKey1 === value1
     --- hashKey2 === value2
     --- hashKey3 === value3
key2 --- hashKey4 === value4
     --- hashKey5 === value5
.
.
.
```
You could also imagine it as a tree with the top level nodes being the Keys, the immediate next level to be hashKeys, and the leaf nodes to be the values. To access `value2`, you would need to have `key1` and `hashKey2`.

Our example is a bit incorrect, as a `User` could have same key=`firstName` and hashKey=`lastName` as another user, and Redis will overwrite `value`. However, for brevity, we will assume there are unique `User`s using our application.

We would now be creating a controller class called `NormalController` which would act as an entry point for our API. We have named it `NormalController` for reasons that will be clear further in this article.

```java
@RestController
@RequestMapping("/normal")
public class NormalController {

    private final NormalService normalService;

    @Autowired
    public NormalController(NormalService normalService) {
        this.normalService = normalService;
    }

    @GetMapping("/get")
    public User get(@RequestParam("firstName") String firstName, @RequestParam("lastName") String lastName) {
        return normalService.get(firstName, lastName);
    }

    @PostMapping("/insert")
    public void insert(@RequestBody User user) {
        normalService.put(user);
    }

    @PostMapping("/delete")
    public void delete(@RequestParam("firstName") String firstName) {
        normalService.delete(firstName);
    }
}
```

`NormalController` also has a service named `NormalService` which is `Autowired`.
The class should be defined in a new packaged named `controller` after which the package structure would look like

```txt
->src
  ->main
    ->java
      ->com.darshitpp.redis.redisutil
        ->configuration
        ->domain
        ->controller
```

Our basic operations would be simple CRUD like operations which `NormalService` implements using a custom `Operations` interface.

```java
public interface Operations {
    User get(String firstName, String lastName);
    void put(User user);
    void delete(String firstName);
}
```

To use Lettuce in our application, we need to do a couple of more things though. Just like to access JDBC, there's a provision for a `JdbcTemplate`, you must similarly use a `RedisTemplate` to operate on Redis. We must also define in what format will Redis store the data inside it. By default, it stores data as a String. However, know that you'll be storing `User` in Redis, and in order to facilitate the storage and fetch from Redis, you would need a way through which Redis will be able to identify and convert it back to the appropriate type of data you want. 

Think of this as talking with someone who doesn't know the same language as you do. If you want to communicate with someone who only speaks Spanish, you would need to find a translator who would convert English into Spanish for you. This process of conversion and recovery is known as Serialization and Deserialization.

English to Spanish = Serialization
Spanish to English = Deserialization

Thus, we need a translator or a Serializer in our case too. We would be using [Jackson](https://github.com/FasterXML/jackson) for this process. Jackson is a nifty library which Spring Boot supports out-of-the-box to handle Json.

We would need to create a Serializer which `implements` `RedisSerializer` for our purposes. In our case, I have created a class `JsonRedisSerializer` inside a new package called `serializer`.

```java
class JsonRedisSerializer<T> implements RedisSerializer<T> {
    public static final Charset DEFAULT_CHARSET;
    private final JavaType javaType;
    private ObjectMapper objectMapper = new ObjectMapper()
            .registerModules(new Jdk8Module(), new JavaTimeModule(), new ParameterNamesModule(JsonCreator.Mode.PROPERTIES))
            .configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, true)
            .configure(SerializationFeature.FAIL_ON_EMPTY_BEANS, false)
            .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
            .setSerializationInclusion(JsonInclude.Include.NON_NULL);

    public JsonRedisSerializer(Class<T> type) {
        this.javaType = JavaTypeHandler.getJavaType(type);
    }

    public T deserialize(@Nullable byte[] bytes) throws SerializationException {
        if (bytes == null || bytes.length == 0) {
            return null;
        } else {
            try {
                return this.objectMapper.readValue(bytes, 0, bytes.length, this.javaType);
            } catch (Exception ex) {
                throw new SerializationException("Could not read JSON: " + ex.getMessage(), ex);
            }
        }
    }

    public byte[] serialize(@Nullable Object value) throws SerializationException {
        if (value == null) {
            return new byte[0];
        } else {
            try {
                return this.objectMapper.writeValueAsBytes(value);
            } catch (Exception ex) {
                throw new SerializationException("Could not write JSON: " + ex.getMessage(), ex);
            }
        }
    }
    
    static {
        DEFAULT_CHARSET = StandardCharsets.UTF_8;
    }

}
```

As you can see, it has two methods called `serialize` and `deserialize`. Each of these methods use the Jackson's `ObjectMapper` for conversion.

There is also a class named `JavaTypeHandler` which helps you get the Type of the object you're trying to serialize. 
```java
final class JavaTypeHandler {

    static <T> JavaType getJavaType(Class<T> clazz) {
        return TypeFactory.defaultInstance().constructType(clazz);
    }

}
```

Consequently, we would also need a class which returns us a `RedisTemplate` which utilizes this serializer. I would name this class `RedisSerializationBuilder`.

```java
public final class RedisSerializationBuilder {

    public static <T> RedisTemplate<String, T> getNormalRedisTemplate(final LettuceConnectionFactory factory, final Class<T> clazz) {
        JsonRedisSerializer<T> jsonRedisSerializer = new JsonRedisSerializer<>(clazz);

        RedisTemplate<String, T> redisTemplate = new RedisTemplate<>();
        redisTemplate.setConnectionFactory(factory);
        redisTemplate.setDefaultSerializer(RedisSerializer.json());
        redisTemplate.setKeySerializer(RedisSerializer.string());
        redisTemplate.setValueSerializer(RedisSerializer.string());
        redisTemplate.setHashKeySerializer(RedisSerializer.string());
        redisTemplate.setHashValueSerializer(jsonRedisSerializer);
        redisTemplate.afterPropertiesSet();
        return redisTemplate;
    }

}
```

Notice that the above method will return you a template specific to a particular domain model(in our case, the `User`) using Generics. It also specifies what connection factory is to be used, what should be the default `key`/`value`/`hashKey`/`hashValue` serializers.

Consequently, the `NormalService` looks like 

```java
@Service
public class NormalService implements Operations{

    private final RedisTemplate<String, User> redisTemplate;
    private final HashOperations<String, String, User> hashOperations;

    public NormalService(LettuceConnectionFactory redisConnectionFactory) {
        this.redisTemplate = RedisSerializationBuilder.getNormalRedisTemplate(redisConnectionFactory, User.class);
        this.hashOperations = this.redisTemplate.opsForHash();
    }

    @Override
    public User get(String firstName, String lastName) {
        return hashOperations.get(firstName, lastName);
    }

    @Override
    public void put(User user) {
        hashOperations.put(user.getFirstName(), user.getLastName(), user);
    }

    @Override
    public void delete(String firstName) {
        hashOperations.delete(firstName);
    }
}
```
I then inserted a `User`, using the `POST` method, and URL: `localhost:8080/normalService/insert`
Request Body:
```json
{
  "firstName": "Priscilla",
  "lastName": "Haymes",
  "birthday": "2020-04-12T11:15:00Z"
}
```


If I then run this application for 100 Users, I find the following stats for the memory usage in Redis (I used the `memory stats` command using the `redis-cli`)
```txt
21) "keys.count"
22) (integer) 100
23) "keys.bytes-per-key"
24) (integer) 1044
25) "dataset.bytes"
26) (integer) 32840
```
Using the `hgetall` command for a key gives me
```txt
127.0.0.1:6379>hgetall "Priscilla"
1) "Haymes"
2) "{\"firstName\":\"Priscilla\",\"lastName\":\"Haymes\",\"birthday\":1586690100000}"
```
Notice that `2)` gives us the actual type of data stored in Redis -> Json!

Our basic structure for further optimizations is in place! Yay!

# Optimization

[MessagePack](https://msgpack.org/) is here to the rescue! As I said, you'd need a "transalation" mechanism. What if the translator is an expert, and converts your English into Spanish in as few words as possible? MessagePack is the same!

You would need to add two more dependencies in your `pom.xml` file.

```xml
	<dependency>
		<groupId>org.msgpack</groupId>
		<artifactId>msgpack-core</artifactId>
		<version>0.8.20</version>
	</dependency>
	<dependency>
		<groupId>org.msgpack</groupId>
		<artifactId>jackson-dataformat-msgpack</artifactId>
		<version>0.8.20</version>
	</dependency>
```

We create a controller called `MsgPackController` and a service called `MsgPackService` almost similar to `NormalController` and `NormalService`. We  would create a `MsgPackSerializer` to serialize using MessagePack.

```java
class MsgPackRedisSerializer<T> implements RedisSerializer<T> {
    public static final Charset DEFAULT_CHARSET;
    private final JavaType javaType;
    private ObjectMapper objectMapper = new ObjectMapper(new MessagePackFactory())
            .registerModules(new Jdk8Module(), new JavaTimeModule())
            .configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, true)
            .configure(SerializationFeature.FAIL_ON_EMPTY_BEANS, false)
            .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
            .setSerializationInclusion(JsonInclude.Include.NON_NULL);

    public MsgPackRedisSerializer(Class<T> type) {
        this.javaType = JavaTypeHandler.getJavaType(type);
    }

    public T deserialize(@Nullable byte[] bytes) throws SerializationException {
        if (bytes == null || bytes.length == 0) {
            return null;
        } else {
            try {
                return this.objectMapper.readValue(bytes, 0, bytes.length, this.javaType);
            } catch (Exception ex) {
                throw new SerializationException("Could not read MsgPack JSON: " + ex.getMessage(), ex);
            }
        }
    }

    public byte[] serialize(@Nullable Object value) throws SerializationException {
        if (value == null) {
            return new byte[0];
        } else {
            try {
                return this.objectMapper.writeValueAsBytes(value);
            } catch (Exception ex) {
                throw new SerializationException("Could not write MsgPack JSON: " + ex.getMessage(), ex);
            }
        }
    }
    
    static {
        DEFAULT_CHARSET = StandardCharsets.UTF_8;
    }

}
```

The only major noticeable change is an instance of `MessagePackFactory` being passed into the `ObjectMapper`. This would act as a bridge between binary and String formats of data between Redis and our Spring Boot application.

Testing our changes (after clearing the previously utilized storage from redis gives us the following:

```txt
127.0.0.1:6379> hgetall "Priscilla"
1) "Haymes"
2) "\x83\xa9firstName\xa9Priscilla\xa8lastName\xa6Haymes\xa8birthday\xcf\x00\x00\x01qn\x19\x8b "

127.0.0.1:6379> memory stats
.
.
.
21) "keys.count"
22) (integer) 100
23) "keys.bytes-per-key"
24) (integer) 876
25) "dataset.bytes"
26) (integer) 15976
```

Compare the `dataset.bytes` from the current memory to the previously recorded one. 15976 bytes vs 32840 bytes, nearly 50% reduction already!

But wait, we can reduce it further. How, you ask. Compression! What if we compress the data and then store it? In our case it would work! This time, [Snappy](https://google.github.io/snappy/) to the rescue!

Your first question after this would be: compression and decompression takes time. Wouldn't it be detrimental on production? Snappy has the answer to this too.

>It does not aim for maximum compression, or compatibility with any other compression library; instead, it aims for very high speeds and reasonable compression.

Using Snappy is also as simple as adding the dependency in `pom.xml`, and a couple of lines of code changes. Just add `Snappy.compress` while serialization and `Snappy.decompress` while deserialization.
```xml
	<dependency>
		<groupId>org.xerial.snappy</groupId>
		<artifactId>snappy-java</artifactId>
		<version>1.1.7.3</version>
	</dependency>
```

Testing it again with the same inputs returns the following
```txt
127.0.0.1:6379> hgetall "Priscilla"
1) "Haymes"
2) "7\\\x83\xa9firstName\xa9Priscilla\xa8la\t\x13`\xa6Haymes\xa8birthday\xcf\x00\x00\x01qn\x19\x8b "

127.0.0.1:6379> memory stats
.
.
.
21) "keys.count"
22) (integer) 100
23) "keys.bytes-per-key"
24) (integer) 873
25) "dataset.bytes"
26) (integer) 15720
``` 
You can see that the size of the data set is smaller, 15720 bytes vs 15976 bytes, a marginal difference, but with larger amounts of data, this difference increases.

In my case, cleaning and restructuring the data, and utilizing the above techniques, we brought down the memory usage from 2GB to less than 500MB.

The full code can be found on my Github for [redis-util](https://github.com/darshitpp/redis-util).

------

Special mention to Rahul Chopda ([@_RahulChopda](https://twitter.com/_RahulChopda)) for his guidance! You have been a best mentor anyone could ask for! 