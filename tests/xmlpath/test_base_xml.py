import textwrap
import unittest


class BaseXmlTest(unittest.TestCase):
    xml_template = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <properties>
        <revision>UNSET</revision>
    </properties>
</project>    
"""

    original_full_xml_str = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <!--
        This pom contains the ORIGINAL_VALUE in multiple XML-paths.
        The Goal is to control the path to be replaced without changing any other's path version nor the formatting.
    -->
    <project xmlns="http://maven.apache.org/POM/4.0.0"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">

        <parent>
            <groupId>com.mycompany.app</groupId>
            <artifactId>my-app</artifactId>
            <version>ORIGINAL_VALUE</version>
        </parent>

        <modelVersion>4.0.0</modelVersion>
        <groupId>com.dummy</groupId>
        <artifactId>java-web-project</artifactId>
        <packaging>war</packaging>
        <version>ORIGINAL_VALUE</version>

        <properties>
            <revision>ORIGINAL_VALUE</revision>
            <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
            <maven.compiler.source>1.8</maven.compiler.source>
            <maven.compiler.target>1.8</maven.compiler.target>
            <spring.version>ORIGINAL_VALUE</spring.version>
            <!-- Assure the dot in XPath ./properties/spring.version is not an any-match like in regex. -->
            <spring_version>ORIGINAL_VALUE</spring_version>
            <jetty.maven.plugin-version>ORIGINAL_VALUE</jetty.maven.plugin-version>
        </properties>

        <dependencies>
            <!-- This is a dependency which version is set by a property. -->
            <dependency>
                <groupId>org.springframework</groupId>
                <artifactId>spring-webmvc</artifactId>
                <version>${spring.version}</version>
            </dependency>
            <!-- This is a dependency with an explicit version. -->
            <dependency>
                <groupId>org.springframework</groupId>
                <artifactId>spring-test</artifactId>
                <version>ORIGINAL_VALUE</version>
            </dependency>
            <!-- This is another dependency with an explicit version. -->
            <dependency>
                <groupId>ch.qos.logback</groupId>
                <artifactId>logback-classic</artifactId>
                <version>ORIGINAL_VALUE</version>
            </dependency>
        </dependencies>

        <build>
            <finalName>java-web-project</finalName>
            <plugins>
                <!-- This is a plugin which version is set by a property. -->
                <plugin>
                    <groupId>org.eclipse.jetty</groupId>
                    <artifactId>jetty-maven-plugin</artifactId>
                    <version>${jetty.maven.plugin-version}</version>
                </plugin>
                <!-- This is a plugin with an explicit version. -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-surefire-plugin</artifactId>
                    <version>ORIGINAL_VALUE</version>
                </plugin>
                <!-- This is another plugin with an explicit version. -->
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-war-plugin</artifactId>
                    <version>ORIGINAL_VALUE</version>
                </plugin>
            </plugins>
        </build>

    </project>
    """)