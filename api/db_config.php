<?php
/* ==========================================================================
   Shrimp Farm Record Management System - XAMPP PHP Database Connection
   ========================================================================== */

$host = 'localhost';
$user = 'root';
$pass = ''; // Default XAMPP MySQL password is empty
$dbname = 'shrimp_farm_db';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false
    ]);
} catch (PDOException $e) {
    // Return JSON error response if accessed via API request
    header('Content-Type: application/json');
    echo json_encode([
        'status' => 'error',
        'message' => 'Database connection failed: ' . $e->getMessage()
    ]);
    exit;
}
?>
