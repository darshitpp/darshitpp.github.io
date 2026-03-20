---
title: "A self-hosted Java based URL shortener"
date: 2020-09-15T11:30:03+00:00
tags: ["url-shortener", "just", "spring-boot", "redis", "docker"]
showToc: true
TocOpen: false
draft: true
comments: true
description: "Desc Text."
disableShare: false
disableHLJS: false
cover:
    image: "<image path/url>" # image path/url
    alt: "<alt text>" # alt text
    caption: "<text>" # display caption under cover
    relative: false # when using page bundles set this to true
    hidden: true # only hide on current single page

---

Implementing a URL shortener service is quite trivial. It usually comprises of 4 steps.

1. Generate a random string
2. Map it to the URL you want to shorten 
3. Store the mapping in a database
4. Fetch the URL from the random string

A simple approach would just be to associate a number with each request. Suppose if you want to shorten `https://google.com`, you can just associate it to a number `1` and store it in your DB.

```
1 -> https://google.com
```

Unfortunately, the problem with this is after a point, there will be lot of numbers of size even larger than the original URL itself. Moreover, the numbers could be "reproduced" by anyone. Someone could just bruteforce and request all the URLs by generating all the numbers sequentially.

Hence, a better approach is to not use sequential numbers, and instead generate random ones over a range. If random numbers are mapped to the URL, it would decrease the chances of someone trying to bruteforce all the URLs stored. We can use rate limiting to achieve this. 

However, even the random numbers can get large to the point that the resulting "short" URL is longer than the original URL. To mitigate this, we utilize converting the numbers to a format called Base62. This is the algorith we can use to "shorten" the URLs as a larger number can be represented as a smaller string.

A pseudocode for Base62 conversion is 
```java

public static final char[] BASE62_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789".toCharArray();

public static final int SIXTY_TWO = 62;

public static String convertToBase62(final String stringNumber) {
    int charPos = stringNumber.length() - 1;
    char[] buffer = new char[stringNumber.length()];
    BigInteger number = new BigInteger(stringNumber);
    BigInteger base = BigInteger.valueOf(SIXTY_TWO);
    while (number.compareTo(base) >= 0) {
        buffer[charPos--] = BASE62_CHARS[number.mod(base).intValue()];
        number = number.divide(base);
    }
    buffer[charPos] = BASE62_CHARS[number.intValue()];
    
    return new String(buffer, charPos, stringNumber.length() - charPos);
}

```

Put simply, if you wanted to convert a number 5000 to Base62, you'd do the following steps:

Iteration 1:
```
1. 5000 %   62 = 40 => store `[40]`
2. 5000 /   62 = 80
```

Iteration 2:
```
3. 80   %   62 = 18 => store `[18, 40]`
4. 80   /   62 = 1
```

Iteration 3:
```
5. 1    %   62 = 1  => store `[1, 18, 40]`
6. 1    /   62 = 0
```

If we select `1`, `18`, and `40` from the Base62 character set, we get the characters, 

`[1]`=`b`

`[18]`=`s`

`[40]`=`O` 

which gives us the string `bsO`.





