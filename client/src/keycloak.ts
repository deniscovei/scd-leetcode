import Keycloak from 'keycloak-js';

const keycloak = new Keycloak({
  // Keycloak is mapped to host port 8081 in docker-compose on this machine
  url: 'http://localhost:8081/',
  realm: 'scd-leetcode',
  clientId: 'scd-leetcode-client'
});

export default keycloak;
