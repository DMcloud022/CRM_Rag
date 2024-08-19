import React from "react";
import { TouchableOpacity, Text, Image } from "react-native";
import { TouchableOpacityProps } from "react-native";
import { ImageSourcePropType } from "react-native";

interface LoginButtonProps extends TouchableOpacityProps {
  providerName: string;
  backgroundColor: string;
  logoSource: ImageSourcePropType;
  textColor?: string;
}

const LoginButton: React.FC<LoginButtonProps> = ({
  providerName,
  backgroundColor,
  logoSource,
  textColor = "text-white", // Default to white if not provided
  onPress,
  ...props
}) => {
  return (
    <TouchableOpacity
      className={`flex-row items-center py-2 px-5 rounded-lg ${backgroundColor}`}
      onPress={onPress}
      {...props}
    >
      <Image source={logoSource} className="w-6 h-6 mr-3 ml-[-5]" />
      <Text className={`${textColor} text-base font-bold`}>
        Log in with {providerName}
      </Text>
    </TouchableOpacity>
  );
};

export default LoginButton;
