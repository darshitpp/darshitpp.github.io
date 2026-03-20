+++
title = "Using IntelliJ IDEA Live Templates"
date = 2019-09-01T14:02:10+05:30
images = []
tags = ["java", "intellij", "logger", "productivity"]
categories = []
draft = false
+++

IntelliJ IDEA is an awesome IDE, and a lesser known and used feature is Live Templates.

Live Templates enable you to use code snippets with just a few keystrokes. A lot of great ones are provided out-of-the-box by IntelliJ. You can view them using the shortcut press `Double Shift` and then typing `Live Templates`. The shortcut works regardless of the OS you're currently using (and I am too lazy to specify OS specific menus).

Some of the examples of Live Templates are:

Typing `psvm` replaces it with 
```java
public static void main(String[] args){
  
}
```

Typing `psfs` magically turns it into
```java
public static final String
```

I was recently refactoring a lot of `class`es and I had to replace a lot of legacy logging initialization statements to using `slf4j` logging library like the following:

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LoggerTest {
    public static final Logger logger = LoggerFactory.getLogger(LoggerTest.class);
}
```
I had more than 30 different classes to refactor as the above, and I certainly didn't want to painstakingly write everything by hand again (confirms that I'm lazy).

Fortunately, IntelliJ Live Templates came to my rescue! I fired up the Live Templates menu using the shortcut mentioned above, and clicked on the `+` button at the top right.

![Check the `+` on the top right!](https://imgur.com/6bbbZpm.png)

I then clicked on `Live Template` button. The UI now points to the bottom which asks you to put an abbreviation.

![Abbreviation](https://imgur.com/vSuAw6t.png)

Let's input the abbreviation as `psfl` which stands for `public static final Logger`, which can be also put in the description.

Write the following code in the Template text box:
```java
public static final Logger logger = LoggerFactory.getLogger();
```
![Template](https://imgur.com/ZTj7Wj7.png)

But hang on, the IDE gives us a warning to define a context where it would be used at. We want the template to be only used in Java, so we click on the `Define` button, and select `Java`.

![Java only template](https://imgur.com/6wXTcV1.png)

You may now notice the IDE now applies syntax highlighting on the template.

Wait, we are still not there yet. I certainly don't want to manually write every class name inside the `getLogger` function! At this point, I was not sure how I could achieve that. Cue in a bit of googling, stackoverflow again came to the rescue.

I found the following answer: https://stackoverflow.com/a/8552882/4840501

```java
public static final org.slf4j.Logger logger =
org.slf4j.LoggerFactory.getLogger($CLASS_NAME$);
$END$
```

So I copy-pasted the code in my template screen(what did you expect? :P)

You'd then need to define what `$CLASS_NAME$` means. To do that, click on the `Edit Variables` button and select `className()` in the `Expression` box.

![Select `className()`](https://imgur.com/mTJoIvT.png)

The `$END$` variable means where you want your cursor at, after the template is applied.

Click on `Apply` and `Ok`.

We're done!

Fire up your classes and refactor with 10x speed!

Relevant link: https://www.jetbrains.com/help/idea/creating-and-editing-live-templates.html