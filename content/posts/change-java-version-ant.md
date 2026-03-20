+++
title = "How to change Java Version/JAVA_HOME for Ant?"
date = 2020-06-15T10:40:40+05:30
tags = ["java", "linux", "ant"]
categories = []
draft = false
+++

I wrote this earlier on a [Github gist](https://gist.github.com/darshitpp/f8017cdb61f4056c100edbf0182a6be0), but putting it here for a consolidated reference.

## Want to change Java Version/JAVA_HOME for Ant builds?

1. Open `~/.antrc` file by running `vim ~/.antrc`
2. Add `JAVACMD=<NEW_JAVA_HOME>/bin/java` and save

> The Ant wrapper script for Unix will source (read and evaluate) the file ~/.antrc before it does anything.
On Windows, the Ant wrapper batch-file invokes %HOME%\antrc_pre.bat at the start and %HOME%\antrc_post.bat at the end. 
You can use these files, for example, to set/unset environment variables that should only be visible during the execution of Ant.

>The wrapper scripts use the following environment variables (if set):
>* JAVACMD—full path of the Java executable. Use this to invoke a different JVM than JAVA_HOME/bin/java(.exe).
>* ANT_OPTS—command-line arguments that should be passed to the JVM. For example, you can define system properties or set the maximum Java heap size here.
>* ANT_ARGS—Ant command-line arguments. For example, set ANT_ARGS to point to a different logger, include a listener, and to include the `-find` flag. Note: If you include -find in ANT_ARGS, you should include the name of the build file to find, even if the file is called build.xml.

Source: https://ant.apache.org/manual/running.html
