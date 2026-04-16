// Import necessary libraries
import * as BABYLON from 'babylonjs';

// Create a new scene
const game = new BABYLON.Scene();
const engine = new BABYLON.Engine();
const canvas = document.getElementById('canvas');
const scene = game.getScene();

// Create a new camera
const camera = new BABYLON.ArcRotateCamera('Camera', 0, 0, 10, new BABYLON.Vector3(0, 1.7, 0), scene);
camera.attachControl(canvas, true);

camera.position.x = 0;
camera.position.y = 1.7;
camera.position.z = 10;

// Create a new light
const light = new BABYLON.PointLight('light', new BABYLON.Vector3(0, 1.7, 0), scene);
light.intensity = 1;
nlight.diffuse = new BABYLON.Color3(1, 1, 1);

// Create a new cube
const cube = new BABYLON.MeshBuilder.CreateBox('cube', { height: 1, width: 1, depth: 1 }, scene);
cube.position.x = 0;
cube.position.y = 1.7;
cube.position.z = 0;
cube.rotation.x = 0;
cube.rotation.y = 0;
cube.rotation.z = 0;

cube.material = new BABYLON.DefaultMaterial('material', scene);
cube.material.diffuseColor = new BABYLON.Color3(1, 0, 0);

game.runRenderLoop(() => {
  engine.render();
});

engine.registerBeforeRun(() => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
});

engine.run RenderLoop();
