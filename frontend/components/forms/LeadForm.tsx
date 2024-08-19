import React from "react";
import {
  View,
  TextInput,
  Text,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from "react-native";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { leadFormSchema, LeadFormSchema } from "@/validation/leadFormSchema";
import { Href, router } from "expo-router";
// import { submitFormData } from "../api/backend";

const LeadForm: React.FC<{ redirectTo: string }> = ({ redirectTo }) => {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<LeadFormSchema>({
    resolver: zodResolver(leadFormSchema),
    defaultValues: {
      name: "",
      email: "",
      phone: "",
      company: "",
      position: "",
      linkedin_profile: "",
      public_data: "",
    },
  });

  const onSubmit = async (data: LeadFormSchema) => {
    console.log("code submit logic here");
    router.replace(redirectTo as Href<string>);

    // try {
    //   const result = await submitFormData(data);
    //   console.log('Data submitted successfully:', result);
    // } catch (error) {
    //   console.error('Submission failed:', error);
    // }
  };

  return (
    <KeyboardAvoidingView
      className="flex-1"
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={Platform.OS === "ios" ? 64 : 0}
    >
      <View className="flex-1 p-10">
        <View className="flex-1">
          {/* Name Input */}
          <View className="mb-3">
            <Text className="text-gray-800 font-medium mb-1">Name</Text>
            <Controller
              control={control}
              name="name"
              render={({ field: { onChange, onBlur, value } }) => (
                <TextInput
                  className="border border-gray-300 p-2 rounded"
                  placeholder="Enter your name"
                  placeholderTextColor="gray"
                  onChangeText={onChange}
                  onBlur={onBlur}
                  value={value}
                />
              )}
            />
            {errors.name && (
              <Text className="text-red-500 mt-1">{errors.name.message}</Text>
            )}
          </View>
          {/* Email Input */}
          <View className="mb-3">
            <Text className="text-gray-800 font-medium mb-1">Email</Text>
            <Controller
              control={control}
              name="email"
              render={({ field: { onChange, onBlur, value } }) => (
                <TextInput
                  className="border border-gray-300 p-2 rounded"
                  placeholder="Enter your email"
                  placeholderTextColor="gray"
                  onChangeText={onChange}
                  onBlur={onBlur}
                  value={value}
                  keyboardType="email-address"
                />
              )}
            />
            {errors.email && (
              <Text className="text-red-500 mt-1">{errors.email.message}</Text>
            )}
          </View>
          {/* Phone Input */}
          <View className="mb-3">
            <Text className="text-gray-800 font-medium mb-1">Phone</Text>
            <Controller
              control={control}
              name="phone"
              render={({ field: { onChange, onBlur, value } }) => (
                <TextInput
                  className="border border-gray-300 p-2 rounded"
                  placeholder="Enter your phone number"
                  placeholderTextColor="gray"
                  onChangeText={onChange}
                  onBlur={onBlur}
                  value={value}
                  keyboardType="phone-pad"
                />
              )}
            />
            {errors.phone && (
              <Text className="text-red-500 mt-1">{errors.phone.message}</Text>
            )}
          </View>
          {/* Company Input */}
          <View className="mb-3">
            <Text className="text-gray-800 font-medium mb-1">Company</Text>
            <Controller
              control={control}
              name="company"
              render={({ field: { onChange, onBlur, value } }) => (
                <TextInput
                  className="border border-gray-300 p-2 rounded"
                  placeholder="Enter your company"
                  placeholderTextColor="gray"
                  onChangeText={onChange}
                  onBlur={onBlur}
                  value={value}
                />
              )}
            />
            {errors.company && (
              <Text className="text-red-500 mt-1">
                {errors.company.message}
              </Text>
            )}
          </View>
          {/* Position Input */}
          <View className="mb-3">
            <Text className="text-gray-800 font-medium mb-1">Position</Text>
            <Controller
              control={control}
              name="position"
              render={({ field: { onChange, onBlur, value } }) => (
                <TextInput
                  className="border border-gray-300 p-2 rounded"
                  placeholder="Enter your position"
                  placeholderTextColor="gray"
                  onChangeText={onChange}
                  onBlur={onBlur}
                  value={value}
                />
              )}
            />
            {errors.position && (
              <Text className="text-red-500 mt-1">
                {errors.position.message}
              </Text>
            )}
          </View>
          {/* LinkedIn Profile Input */}
          <View className="mb-3">
            <Text className="text-gray-800 font-medium mb-1">
              LinkedIn Profile URL
            </Text>
            <Controller
              control={control}
              name="linkedin_profile"
              render={({ field: { onChange, onBlur, value } }) => (
                <TextInput
                  className="border border-gray-300 p-2 rounded"
                  placeholder="Enter your LinkedIn profile URL"
                  placeholderTextColor="gray"
                  onChangeText={onChange}
                  onBlur={onBlur}
                  value={value}
                />
              )}
            />
            {errors.linkedin_profile && (
              <Text className="text-red-500 mt-1">
                {errors.linkedin_profile.message}
              </Text>
            )}
          </View>
          {/* Public Data Input */}
          <View className="mb-3">
            <Text className="text-gray-800 font-medium mb-1">
              Public Data (JSON format)
            </Text>
            <Controller
              control={control}
              name="public_data"
              render={({ field: { onChange, onBlur, value } }) => (
                <TextInput
                  className="border border-gray-300 p-2 rounded"
                  placeholder="Enter public data in JSON format"
                  placeholderTextColor="gray"
                  onChangeText={onChange}
                  onBlur={onBlur}
                  value={value}
                />
              )}
            />
          </View>
          {/* Submit Button */}
          <TouchableOpacity
            className="bg-blue-600 py-2 px-4 rounded mt-4"
            onPress={handleSubmit(onSubmit)}
          >
            <Text className="text-white text-center font-bold">Submit</Text>
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

export default LeadForm;
