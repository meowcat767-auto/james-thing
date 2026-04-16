// Import necessary libraries
import * as THREE from 'three';
import levels from './levels.json';

// Create the game scene
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({
  canvas: document.getElementById('canvas'),
  antialias: true
});

// Create a cube
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

camera.position.z = 5;

// Load levels
let currentLevel = 0;
let levelData = levels[currentLevel];

// Create obstacles
levelData.obstacles.forEach((obstacle) => {
  const obstacleGeometry = new THREE.BoxGeometry(1, 1, 1);
  const obstacleMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
  const obstacleMesh = new THREE.Mesh(obstacleGeometry, obstacleMaterial);
  obstacleMesh.position.x = obstacle.x;
  obstacleMesh.position.y = obstacle.y;
  scene.add(obstacleMesh);
});

// Create goal
const goalGeometry = new THREE.BoxGeometry(1, 1, 1);
const goalMaterial = new THREE.MeshBasicMaterial({ color: 0x0000ff });
const goalMesh = new THREE.Mesh(goalGeometry, goalMaterial);
goalMesh.position.x = levelData.goal.x;
goalMesh.position.y = levelData.goal.y;
scene.add(goalMesh);

// Animation loop
function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
}

animate();

// Add keyboard controls
document.addEventListener('keydown', (event) => {
  if (event.key === 'ArrowUp') {
    cube.position.y += 0.1;
  } else if (event.key === 'ArrowDown') {
    cube.position.y -= 0.1;
  } else if (event.key === 'ArrowLeft') {
    cube.position.x -= 0.1;
  } else if (event.key === 'ArrowRight') {
    cube.position.x += 0.1;
  }
});