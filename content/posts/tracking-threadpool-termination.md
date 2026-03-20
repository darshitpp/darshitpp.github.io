---
title: "Mastering ExecutorService Shutdown: Tracking ThreadPool Termination"
date: 2025-01-04T12:14:21+05:30
draft: false
tags: [ "java", "ExecutorService", "threadpool", "threads", "shutdown"]
comments: true
description: "How do you know if all the tasks in ExecutorService have completed?"
---

Let's say you want to execute some tasks. Since executing it through a single thread might take you quite some time to get the result, you decide to use the ever dependable `ExecutorService` to process it through multiple threads.

Here's a sample:

```java
public static void main(String[] args) {
    ExecutorService executorService = Executors.newFixedThreadPool(5);
    for (int i = 0; i < 5; i++) {
        int temp = i;
        executorService.submit(() -> {
            task(temp);
        });
    }
    executorService.shutdown();
    System.out.println("ExecutorService is shutdown");
}

private static void task(int temp) {
    try {
        TimeUnit.SECONDS.sleep(1L);
        System.out.println("Task " + temp + " completed");
    } catch (InterruptedException e) {
        throw new RuntimeException(e);
    }
}
```

Of course, as usual, no example of Threads is ever complete without using "sleep" as an archetype of task execution.

It outputs,
```
ExecutorService is shutdown
Task 1 completed
Task 2 completed
Task 0 completed
Task 4 completed
Task 3 completed
```

Now imagine there's an endless queue of tasks, the number of which you don't know about. Maybe they are determined by the number of entries in a database which get added dynamically.

For example, a bank, wherein which it has to process a number of transactions throughout the day. The transaction end time will be 5 PM, beyond which it will not accept any additional tasks.

However, you do know that the number of tasks will be finite, and *will* end at some point of time.

How do you know the point in time when all the tasks have completed?

If you notice the above code snippet, the `ExecutorService.shutdown()` enables the main thread to exit immediately, but the background threads still process the accepted tasks to completion. Is there a way when you can get notified about the completion?

A couple of solutions come to mind:

1. Use a `CountDownLatch` to count the tasks - but since you don't know the number of tasks, it's impractical to use it.
2. Use `ExecutorService.awaitTermination()`. However, the time here is still undeterministic. You can use a very liberal `ExecutorService.awaitTermination(Long.MAX_VALUE, TimeUnit.DAYS)` or something similar. But that is again a blocking call.

Is there a better way to solve this?

Java does provide a better and relatively unknown way to get around this. The "trick" here is to know that `Executors.newFixedThreadPool` is essentially a `ThreadPoolExecutor` with predefined values. Let's check the implementation of `Executors.newFixedThreadPool`.

```java
public static ExecutorService newFixedThreadPool(int nThreads) {
    return new ThreadPoolExecutor(nThreads, nThreads,
                                  0L, TimeUnit.MILLISECONDS,
                                  new LinkedBlockingQueue<Runnable>());
}
```

I really recommend to read the doc for `ThreadPoolExecutor` [here](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/ThreadPoolExecutor.html). `ExecutorService` is a convenient wrapper over `ThreadPoolExecutor`.

> ... programmers are urged to use the more convenient `Executors` factory methods `Executors.newCachedThreadPool()` (unbounded thread pool, with automatic thread reclamation), `Executors.newFixedThreadPool(int)` (fixed size thread pool) and `Executors.newSingleThreadExecutor()` (single background thread), that preconfigure settings for the most common usage scenarios.


The section that will help us resolve out problem is:
> #### Hook methods

> This class provides protected overridable `beforeExecute(Thread, Runnable)` and `afterExecute(Runnable, Throwable)` methods that are called before and after execution of each task. These can be used to manipulate the execution environment; for example, reinitializing ThreadLocals, gathering statistics, or adding log entries. Additionally, method `terminated()` can be overridden to perform any special processing that needs to be done once the Executor has fully terminated.


We can use the `terminated` method to notify us of the same! But how do we use it?


```java
public static void main(String[] args) {
    ExecutorService executorService = new ThreadPoolExecutor(5, 5,
            0L, TimeUnit.MILLISECONDS,
            new LinkedBlockingQueue<>()) {
        @Override
        protected void terminated() {
            super.terminated();
            System.out.println("ExecutorService is terminated");
        }
    };
    for (int i = 0; i < 5; i++) {
        int temp = i;
        executorService.submit(() -> {
            task(temp);
        });
    }
    executorService.shutdown();
    System.out.println("ExecutorService is shutdown");
}

private static void task(int temp) {
    try {
        TimeUnit.SECONDS.sleep(1L);
        System.out.println("Task " + temp + " completed");
    } catch (InterruptedException e) {
        throw new RuntimeException(e);
    }
}
```

If you do not prefer Anonymous classes (like me), you can always extend `ThreadPoolExecutor` yourself to create a custom one.

```java
public static void main(String[] args) {
    ExecutorService executorService = getThreadPoolExecutor();
    for (int i = 0; i < 5; i++) {
        int temp = i;
        executorService.submit(() -> {
            task(temp);
        });
    }
    executorService.shutdown();
    System.out.println("ExecutorService is shutdown");
}

private static ThreadPoolExecutor getThreadPoolExecutor() {
    return new CustomThreadPoolExecutor(5, 5,
            0L, TimeUnit.MILLISECONDS,
            new LinkedBlockingQueue<>());
}

static class CustomThreadPoolExecutor extends ThreadPoolExecutor {
    public CustomThreadPoolExecutor(int corePoolSize, int maximumPoolSize, long keepAliveTime, TimeUnit unit, BlockingQueue<Runnable> workQueue) {
        super(corePoolSize, maximumPoolSize, keepAliveTime, unit, workQueue);
    }

    @Override
    protected void terminated() {
        super.terminated();
        System.out.println("ExecutorService is terminated");
    }
}

private static void task(int temp) {
    try {
        TimeUnit.SECONDS.sleep(1L);
        System.out.println("Task " + temp + " completed");
    } catch (InterruptedException e) {
        throw new RuntimeException(e);
    }
}
```

Here's the output to verify if it works as per our expectations.

```
ExecutorService is shutdown
Task 0 completed
Task 3 completed
Task 2 completed
Task 4 completed
Task 1 completed
ExecutorService is terminated
```

What are some other relatively unknown snippets you use? Let me know in the comments!

