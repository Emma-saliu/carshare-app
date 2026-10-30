import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { router } from 'expo-router';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert(
        'Missing information',
        'Please enter your email and password.'
      );
      return;
    }

    try {
      const response = await fetch(
        'http://192.168.1.106:5001/api/login',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email,
            password,
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        router.replace({
          pathname: '/dashboard',
          params: {
            firstName: data.user.firstName,
            userId: String(data.user.id),
          },
        });
      } else {
        Alert.alert(
          'Login failed',
          data.message || 'Unable to login.'
        );
      }
    } catch (error) {
      console.log(error);

      Alert.alert(
        'Connection error',
        'Could not connect to the CarShare server.'
      );
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={styles.form}>
        <Text style={styles.title}>Login</Text>

        <TextInput
          style={styles.input}
          placeholder="Email"
          placeholderTextColor="#777777"
          keyboardType="email-address"
          autoCapitalize="none"
          value={email}
          onChangeText={setEmail}
        />

        <TextInput
          style={styles.input}
          placeholder="Password"
          placeholderTextColor="#777777"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
        />

        <Pressable
          style={styles.loginButton}
          onPress={handleLogin}
        >
          <Text style={styles.loginButtonText}>
            Login
          </Text>
        </Pressable>

        <Pressable onPress={() => router.back()}>
          <Text style={styles.backText}>
            Back
          </Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
  },

  form: {
    padding: 24,
  },

  title: {
    fontSize: 32,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 30,
    color: '#111111',
  },

  input: {
    borderWidth: 1,
    borderColor: '#cccccc',
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    marginBottom: 15,
    color: '#111111',
    backgroundColor: '#ffffff',
  },

  loginButton: {
    backgroundColor: '#111111',
    padding: 16,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 10,
  },

  loginButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
  },

  backText: {
    fontSize: 16,
    textAlign: 'center',
    marginTop: 20,
    color: '#111111',
  },
});