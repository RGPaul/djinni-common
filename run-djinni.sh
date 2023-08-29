#! /usr/bin/env bash

declare base_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
declare cpp_out="$base_dir/generated-src/cpp"
declare jni_out="$base_dir/generated-src/jni"
declare objc_out="$base_dir/generated-src/objc"
declare objcpp_out="$base_dir/generated-src/objcpp"
declare java_out="$base_dir/generated-src/java/eu/appcom/djinni/common"
declare java_package="eu.appcom.djinni.common"
declare namespace="appcom"
declare objc_prefix="AC"
declare djinni_file="djinni/appcom-common.djinni"
declare yaml_out="."
declare yaml_out_file="appcom-common.yml"

rm -r $base_dir/generated-src/* || true

java -jar bin/djinni.jar \
   --java-out $java_out \
   --java-package $java_package \
   --ident-java-field mFooBar \
   \
   --cpp-out $cpp_out \
   --cpp-namespace $namespace \
   --cpp-optional-template "boost::optional" \
   --cpp-optional-header "<boost/optional.hpp>" \
   \
   --jni-out $jni_out \
   --ident-jni-class NativeFooBar \
   --ident-jni-file NativeFooBar \
   \
   --objc-out $objc_out \
   --objc-type-prefix $objc_prefix \
   \
   --objcpp-out $objcpp_out \
   \
   --idl $djinni_file \
   \
   --yaml-out $yaml_out \
   --yaml-out-file $yaml_out_file
