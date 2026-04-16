// Import necessary libraries
import * as THREE from 'three';

// Create the game scene
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({
  canvas: document.getElementById('canvas'),
  antialias: true
});

// Load textures
const skyTexture = new THREE.TextureLoader().load('assets/textures/sky.png');
const groundTexture = new THREE.TextureLoader().load('assets/textures/ground.png');

// Add skybox
const skyGeometry = new THREE.SkyGeometry();
const skyMaterial = new THREE.SkyMaterial({ skyTexture: skyTexture });
const sky = new THREE.Mesh(skyGeometry, skyMaterial);
scene.add(sky);

// Add ground
const groundGeometry = new THREE.PlaneGeometry(100, 100);
const groundMaterial = new THREE.MeshBasicMaterial({ map: groundTexture });
const ground = new THREE.Mesh(groundGeometry, groundMaterial);
scene.add(ground);

// Create a cube
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

camera.position.z = 5;

// Animation loop
function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
}

animate();