import { StyleSheet, Text, View, Pressable } from 'react-native';
import { router } from 'expo-router';

export default function HomeScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>CarShare</Text>

      <Text style={styles.subtitle}>
        Smart car sharing made simple
      </Text>

      <Pressable
        style={styles.primaryButton}
        onPress={() => router.push('/register')}
      >
        <Text style={styles.primaryButtonText}>Register</Text>
      </Pressable>

      <Pressable
      style={styles.secondaryButton}
      onPress={() => router.push('/login')}
      >

      <Text style={styles.secondaryButtonText}>Login</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },

  title: {
    fontSize: 42,
    fontWeight: 'bold',
    marginBottom: 10,
  },

  subtitle: {
    fontSize: 18,
    marginBottom: 40,
    textAlign: 'center',
  },

  primaryButton: {
    width: '100%',
    padding: 16,
    borderRadius: 10,
    backgroundColor: '#111111',
    alignItems: 'center',
    marginBottom: 14,
  },

  primaryButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
  },

  secondaryButton: {
    width: '100%',
    padding: 16,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#111111',
    alignItems: 'center',
  },

  secondaryButtonText: {
    fontSize: 18,
    fontWeight: '600',
  },
});