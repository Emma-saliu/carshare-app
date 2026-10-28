import {
  View,
  Text,
  Pressable,
  StyleSheet,
} from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';

export default function DashboardScreen() {
  const { firstName, userId } = useLocalSearchParams();

  return (
    <View style={styles.container}>
      <Text style={styles.welcome}>
        Welcome, {firstName || 'User'}!
      </Text>

      <Text style={styles.subtitle}>
        What would you like to do?
      </Text>

      <Pressable
        style={styles.primaryButton}
        onPress={() => router.push('/find-ride')}
      >
        <Text style={styles.primaryButtonText}>
          Find a Ride
        </Text>
      </Pressable>

      <Pressable
      style={styles.secondaryButton}
      onPress={() =>
        router.push({
            pathname: '/offer-ride',
            params: { userId: String(userId) },
        })
        }
        >
  <Text style={styles.secondaryButtonText}>
    Offer a Ride
  </Text>
</Pressable>

      <Pressable
        style={styles.logoutButton}
        onPress={() => router.replace('/')}
      >
        <Text style={styles.logoutText}>
          Logout
        </Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
    padding: 24,
  },

  welcome: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#111111',
    marginBottom: 10,
  },

  subtitle: {
    fontSize: 18,
    color: '#555555',
    marginBottom: 40,
  },

  primaryButton: {
    backgroundColor: '#111111',
    padding: 18,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 15,
  },

  primaryButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
  },

  secondaryButton: {
    borderWidth: 1,
    borderColor: '#111111',
    padding: 18,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 30,
  },

  secondaryButtonText: {
    color: '#111111',
    fontSize: 18,
    fontWeight: '600',
  },

  logoutButton: {
    alignItems: 'center',
  },

  logoutText: {
    color: '#cc0000',
    fontSize: 16,
  },
});