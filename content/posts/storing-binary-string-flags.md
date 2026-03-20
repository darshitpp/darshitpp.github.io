---
title: "Storing Feature Flags as Strings"
date: 2024-01-01T13:11:46+05:30
draft: true
---

You're having a great week -- you just delivered a bug-free feature, and it got deployed onto Prod without an issue. The feature took you some time to design, and without much ado, you reused the existing feature flag logic of your system. The flags are set with user settings so that you could enable or disable the feature on the fly. These settings for your system reside as a JSON value inside Redis. 
The value currently looks like this:
```json
{
  "feature_W": false,
  "feature_X": true,
  "feature_Y": true,
  "feature_Z": false
}
```

You're off to a holiday the next week, and can't stop thinking about it! Unfortunately, your daydream comes to an end as you see a ping on your office messenger. It's your SRE/Ops/Monitoring team. They have noticed a spike in Redis memory usage after the deployment. Their alerts have been set for 80% of total memory assigned for Redis, and the only change in the Redis data was adding the feature flag, like everyone else earlier. "Why should it be me!?", you wonder. Thankfully for you, there is not am immediate need for handling this as the cached data is mostly around static, and does not change frequently. You see one of the following two approaches to handle this:

1. Throw more memory!
2. [Compress the data!](https://darshit.dev/posts/reduce-redis-memory-usage/)

Compressing the data will require changes in the application code. Nobody's got the time for that!

Throwing more memory at it won't be as easy either. Depending on the type of Redis deployment you use (Single Node vs Sentinel vs Cluster), it may require different strategies to handle the additional infra. But, that's not your problem, is it?! ;) What use is of the SRE team!??

Like a seasoned programmer, you decide to push this onto the SRE team to handle this for now. Remember, you have to go on a vacation!! You'll think of a long term approach "later" ;)

You start to think though - could the feature flag implementation have been done better?

# Booleans as Strings

TIL: Apparently, a `boolean`, the size of which we *assume* would take only a single bit, officially [doesn't have a precisely defined size](https://docs.oracle.com/javase/tutorial/java/nutsandbolts/datatypes.html).

> https://docs.oracle.com/javase/specs/jvms/se17/jvms17.pdf#%5B%7B%22num%22%3A4175%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2C72%2C564%2Cnull%5D
> In Oracle’s Java Virtual Machine implementation, boolean arrays in the Java programming language are encoded as Java Virtual Machine byte arrays, using 8 bits per boolean element.

Anyhow, when we store booleans as strings in a data store like in the above case, it invariably turns into a larger size. For example, in Java:
```java
> System.out.println("true".getBytes(StandardCharsets.UTF_8).length); 
=> prints 4

> System.out.println("false".getBytes(StandardCharsets.UTF_8).length); 
=> prints 5
```

Which means, a boolean which should have ideally taken 1 byte, now takes 4-5x more space when serialized as a string! The problem exacerbates when you have lots of flags. Now you know why there was an alert generated earlier.

Is there a better way to store booleans? In Redis, unfortunately no, everything is a String. But how about Java?

# Booleans as... integers?



