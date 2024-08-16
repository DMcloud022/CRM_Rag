import React from "react";
import { TouchableOpacity, Text } from "react-native";

interface ActionButtonProps {
  title: string;
  onPress: () => void;
  style?: string;
}

const ActionButton: React.FC<ActionButtonProps> = ({
  title,
  onPress,
  style,
}) => {
  return (
    <TouchableOpacity
      onPress={onPress}
      className={`p-4 rounded ${style}`}
      style={{ alignItems: "center" }}
    >
      <Text className="text-black">{title}</Text>
    </TouchableOpacity>
  );
};

export default ActionButton;
