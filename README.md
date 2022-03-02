# **CountLinesOfCode v2** (Java-only) 
This app with help you count your lines of code in case you are getting paid for money per line of code or just want to know your actual line count.

> **Made With Python3!**

Here are the things that this app can do:
- Count all the lines of code in the total and each file in the directory, each scanned file, or just a single file.
- Count all the lines that are not user-made, just too small, blank, or comments and output the **Actual Lines of Code** in the directory, each scanned file, or just a single file.
- **Works with GIT!** If you are scanning a git directory, the program will also count all of the sections above for each commit author! *(will not count empty lines)*
- **Easy-to-use!** Just download python while having it in `PATH`, run `setup.bat` and you are good to go!

What the application doesn't cound as an **Actual Line of Code**:
- Obviously, blank lines
- Comments and Comment Blocks
- Auto-generated lines. Examples:
  - ```java
    @Override
    ```
  - ```java
    package xyz.superneon4ik.sub;
    ```
  - ```java
    import xyz.superneon4ik.sub.Amogus;
    ```
- Small lines (less than 3 characters) or one of these:
  ```java
  "}", "});", "};", ");", ")", "]", "];"
  ```

# Several examples of usage
![Example 1](/readme/ex1.png)
![Example 2](/readme/ex2.png)

---
[Support me on Patreon!](https://patreon.com/SuperNeon4ik)

[Check out my LinkTree!](http://superneon4ik.xyz)
